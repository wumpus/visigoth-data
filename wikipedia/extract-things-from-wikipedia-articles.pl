#!/usr/bin/perl

use strict;

use IO::Handle;

# xml dump from https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2

# <page>
#  <title>...</title>
#  <revision>
#   If you see #REDIRECT, punt
#   <text... >
#   </text>
#  </revision
# </page>

my $s = '';

my $count = 0;

while (<>)
{
    $s .= $_;
    if ( m,\Q</page>, )
    {
        process( $s );
        $s = '';
    }
}

sub process
{
    my ( $s ) = @_;
    my $title;

    my $raw = $s;

    ( $title, $s ) = actually_process( $s );

    return if ! defined $s;

    print "$title";

    if ( $title =~ /^(?:User:|Wikipedia:|File:|MediaWiki:|Template:|Help:|Category:|Portal:|Book:|Draft:|EducationProgram:|TimedText:|Module:|Gadget:|Gadget definition:|Topic:|Special:|Media:|Image:)/ )
    {
        print " skipped\n";
        return;
    }
    $title =~ s,/,-,g;

    if ( $ENV{ONE} )
    {
        print $s;
        return;
    }

    # in order to make the output a bit easier to deal wiht, divide it up into batches.
    # (The SSD I'm using can't hold the entire dump... so I tar/rm each batch as I see it's complete.)

    $count += 1;
    my $batch = int( $count / 700_000 );

    mkdir "out/$batch" if ! -d "out/$batch";
    mkdir "raw/$batch" if ! -d "raw/$batch";

    return if -e "out/$batch/$title";

    open my $fd, ">", "out/$batch/$title";
    if ( ! defined $fd )
    {
        print STDERR "error opening file out/$batch/$title: $!";
        return;
    }
    print $fd $s, "\n";
    #$fd->sync or die "fsync on out/$batch/$title: $!\n";
    close $fd or warn "Error closing file out/$batch/$title: $!";

    open my $fd2, ">", "raw/$batch/$title";
    print $fd2 $raw, "\n";
    #$fd2->sync or die "fsync on raw/$batch/$title: $!\n";
    close $fd2 or warn "Error closing file raw/$batch/$title: $!";

    print "\n";
    return;
}

sub actually_process
{
    my ( $s ) = @_;

    return if $s =~ /\Q>#REDIRECT/;

    $s =~ m,\Q<title>\E(.*?)\Q</title>,;
    my $title = $1;
    if ( ! defined $title )
    {
        print STDERR "Failed to find title!\n";
        my @lines = split /\n/, $s;
        foreach my $l ( @lines )
        {
            print STDERR "  candidate: $l\n";
        }
        return;
    }

    # nuke everything outside the <text>
    $s =~ s, .* \<text \s .*? \>,,xms;
    $s =~ s,\Q</text>\E.*,,xms;

    # https://en.wikipedia.org/wiki/Help:Wiki_markup

    # we aren't scared of "
    $s =~ s,\&quot;,",xmsg;

    # remove html comments early; can't overlap with {{}} or <ref> anyway
    {
        # http://www.perlmonks.org/?node_id=285983
        $s =~ s/\&lt\; !(?:--(?:[^-]*|-[^-]+)*--\s*) \&gt\; //xmsg; # yeah, <> are quoted
    }

    # unformat wikilinks and external links
    {
        # because [[File: etc frequently have nested [[]], first try to resolve all the non-namespace [[]]
        # change [[foo]] to foo - no namespaces here
        $s =~ s,\[\[ (?!User:|Wikipedia:|File:|MediaWiki:|Template:|Help:|Category:|Portal:|Book:|Draft:|EducationProgram:|TimedText:|Module:|Gadget:|Gadget definition:|Topic:|Special:|Media:|Image:) ([^\]\|\:]*) \]\],$1,xmsg;
        # change [[foo|bar]] to bar - no namespaces here
        $s =~ s,\[\[ (?!User:|Wikipedia:|File:|MediaWiki:|Template:|Help:|Category:|Portal:|Book:|Draft:|EducationProgram:|TimedText:|Module:|Gadget:|Gadget definition:|Topic:|Special:|Media:|Image:) [^\]\:]* \| ([^\]]*) \]\],$1,xmsg;

        # drop [[Namespace:...]] for all the major namespaces
        # unfortunately these frequently have [[x]] and [[x|x]] in their text! gah. which is why we have the above rules
        #$s =~ s,\[\[ (?:User|Wikipedia|File|MediaWiki|Template|Help|Category|Portal|Book|Draft|EducationProgram|TimedText|Module|Gadget|Gadget definition|Topic|Special|Media|Image) : (?:[^\]]*) \]\],,xmsg;
        $s =~ s,\[\[ (?:User|Wikipedia|File|MediaWiki|Template|Help|Category|Portal|Book|Draft|EducationProgram|TimedText|Module|Gadget|Gadget definition|Topic|Special|Media|Image) : (?:.*?) \]\],,xmsg;
        # XXX bug: <ref> in the caption. ordering issue - fix, stop worrying about ] ?

        # change [[foo]] to foo
        $s =~ s,\[\[ ([^\]\|]*) \]\],$1,xmsg;
        # change [[foo|bar]] to bar ... foo can have multiple |, so be greedy in the correct place ...
        # XXX note that it's legal to have |]], in that case mediawiki manufactures a name, see: https://en.wikipedia.org/wiki/Help:Pipe_trick
        $s =~ s,\[\[ [^\]]* \| ([^\]]*) \]\],$1,xmsg;

        # [http...] (external weblinks)
        # XXX for now, leave anchortext but don't turn into a href
        $s =~ s,(?<!\[) \[ (http[^\ \]]+) \ ([^\]]+) \],$2,xmsg; # with anchortext
        $s =~ s,(?<!\[) \[ (http[^\ \]]+) \],,xmsg; # without anchortext
    }

    # now, these things might nest or be incorrectly overlapped XXX is this true? I think I was looking at an example I caused
    # {{..}} and <ref >...</ref>
    {
        # eat <ref .../>
        $s =~ s,\&lt\; ref \ [^\&]*? / \s* \&gt;,,xmsg; # XXX BUG: fails for refs including &quot ... papered over by &quot -> " above
        # change <ref> to {{
        $s =~ s,\&lt\; ref [^\&]*? \&gt;,\{\{,xmsg; # XXX BUG: fails for refs including &quot ... papered over by &quot -> " above
        # change <\ref> to }}
        $s =~ s,\&lt\; \/ref \&gt;,\}\},xmsg;

        # nuke {{...}} these nest! so do it repeatedly
        for my $i ( 1..5 )
        {
            $s =~ s,\{\{[^\{\}]*\}\},,xmsg;
        }

        # we may still have stray {{ or }}... sigh
        $s =~ s,\{\{,,xmsg;
        $s =~ s,\}\},,xmsg;
    }

    # gallery
    $s =~ s,&lt; gallery .*? /gallery &gt;,,xmsg;

    # Wiki tables {| .* |}
    $s =~ s,\{\| .*? \|\},,xmsg;

    # Drop section titles. XXX switch to html markup?
    $s =~ s/\={2,}//xg; # must be on a single line

    # Nuke huge whitespace, just to make it more human-readable
    $s =~ s/\n{3,}/\n\n/xmsg;

    return ( $title, $s );
}

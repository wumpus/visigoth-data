#!/usr/bin/perl

use strict;

use IO::Handle;

# bzcat enwiki-latest-pages-articles.xml.bz2 | ./extract-things-from-wikipedia-articles.pl | fgrep -v ,, | bzip2 > isbns.csv.bz2
# bzcat enwiki-latest-pages-articles.xml.bz2 | ./extract-things-from-wikipedia-articles.pl | fgrep    ,, | bzip2 > external-links.bz2

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

    # Wikipedia allows spaces and dashes in ISBNs

    my @isbns = $s =~ m/\b ISBN \s* = \s* ([\d\-\ ]{1,20}X?)/xmsig;
    if ( @isbns )
    {
	for my $i ( @isbns )
	{
	    $i =~ s/-//g;
	    $i =~ s/ //g;
	    print "\"$title\",$i\n"
	}
    }

    my @external_links = $s =~ m,(?<!\[) \[ (https?[^\ \]]+) [\ \]],xmsg;
    if ( @external_links )
    {
	for my $l ( @external_links )
	{
	    print "\"$title\",,$l\n"
	}
    }

    return ( $title, $s );
}

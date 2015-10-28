#!/usr/bin/env perl

# bzcat ~/job/wikipedia/enwiki-20150901-pages-articles.xml.bz2 | ./spit-titles.pl > wikipedia_articles.csv

use strict;

my $title;
my $redirect;

while (<> )
{
    #<title>ArthurKoestler</title>
    if ( m,\Q<title>\E(.*?)\Q</title>, )
    {
        $title = $1;
    }

    #<redirect title="Arthur Koestler" />
    if ( m,\<redirect title=\"([^\"]*?)\", )
    {
        $redirect = $1;
    }

    if ( m,\</page\>, )
    {
        process( $title, $redirect );
        $title = undef;
        $redirect = undef;
    }
}

sub process
{
    my ( $title, $redirect ) = @_;

    return if $title =~ /^(?:User|Wikipedia|File|MediaWiki|Template|Help|Category|Portal|Book|Draft|EducationProgram|TimedText|Module|Gadget|Gadget definition|Topic|Special|Media|Image):/;

#    return if $title =~ /\(/;
#    return if $redirect =~ /\(/; # this throws away redirects to disambig pages, which are important
#    return if $title =~ /\#/; # can't happen?
#    return if $redirect =~ /\#/; # this throws away redirects to page sections
    return if $title =~ /\//;
    return if $redirect =~ /\//;

    my $spaces =()= $title =~ m, ,g;

    $redirect = '' if ! defined $redirect;

    # Yes, titles can have commas in them. But not quotes.
    print "$spaces,\"$title\",\"$redirect\"\n";
}

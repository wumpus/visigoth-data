#!/usr/bin/env perl

use strict;

# https://wikitech.wikimedia.org/wiki/Analytics/Data/Pagecounts-all-sites
# aa %D9%88%D8%A7%D8%B5%D9%81_%D8%A7%D9%84%D8%AD%D9%84%D8%A8%D9%8A 1 4633

my %counts;

while ( <> )
{
    chomp;
    my ( $domain_code, $page_title, $count_views, $total_response_size ) = split;

    next unless $domain_code eq 'en' || $domain_code eq 'en.m';

    next if $page_title =~ /^(?:User|Wikipedia|File|MediaWiki|Template|Help|Category|Portal|Book|Draft|EducationProgram|TimedText|Module|Gadget|Gadget definition|Topic|Special|Media|Image):/;
    next if $page_title =~ /\(/;
    next if $page_title =~ /\//;

    $counts{$page_title} += $count_views;
}

foreach my $t ( sort { $counts{$b} <=> $counts{$a} } keys %counts )
{
    print "$t,$counts{$t}\n";
}

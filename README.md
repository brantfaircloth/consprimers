## build maf from axt files

    for i in /Users/bcf/git/brant/consprimers/data/conserved/input/axt/*.axt; 
    do axtToMaf $i \
        /Users/bcf/git/brant/consprimers/data/conserved/input/taeGut1.sizes \
        /Users/bcf/git/brant/consprimers/data/conserved/input/galGal3.sizes \
        /Users/bcf/git/brant/consprimers/data/conserved/input/$i.maf \
        -tPrefix=taeGut1. -qPrefix=galGal3.;
    done

## scanned the alignment of taeGut1 and galGal3 with:
    
    # scanning parameters were inbuilt in this version
    python summary.py

## determined locations between conserved areas (and duplicates)
    
    python cons_distance_scanner.py

## determined number of regions 200-5000 bp in birdcons.distance table

    select * from distance where \
    (close_target_distance >= 200 and close_target_distance <= 5000) and \
    (close_query_distance >= 200 and close_query_distance <= 5000) and \
    close_target = close_query;

## designed primers for these loci, storing them in the primers table

    python cons_primer_designer.py --configuration=db.conf

used relatively specific primer design criteria (Tm ~ 65; len > 19) in hopes 
of generating pretty specific primers.

## this created many primers - roughly half of regions in the table:

    select count(*) from distance where (close_target_distance >= 200 and \
        close_target_distance <= 5000) and (close_query_distance >= 200 \
        and close_query_distance <= 5000) and close_target = close_query;
    +----------+
    | count(*) |
    +----------+
    |    15851 |
    +----------+

    select count(*) from primers where primer = 0;
    +----------+
    | count(*) |
    +----------+
    |     8032 |
    +----------+


## updated distance table with amplicon averages

    alter table distance add column average_amplicon double;

    update distance set average_amplicon = \
    (close_target_distance+close_query_distance)/2;

## and amplicon confidence intervals

    alter table distance add column average_amplicon_ci double;

    update distance set average_amplicon_ci = \
    round(1.96*(sqrt((pow(close_target_distance - average_amplicon,2) + \
    pow(close_query_distance - average_amplicon,2))/2)/sqrt(2)),2);

## map out primer positions in gallus and zfinch

    python make_primer_bed.py --configuration=db.conf \
        --output=galGal3.primers.200-5000.bed --chicken
    
    python make_primer_bed.py --configuration=db.conf \
        --output=taeGut1.primers.200-5000.bed

## make a BED file for the cons regions ##

    python make_cons_bed.py --conf=db.conf --cons-min=200 --cons-max=5000

## get the amplicons created from each of the primers ##

    python make_amplicons_from_primers.py 
        --input=data/conserved/output/galGal3.primers.200-5000.bed 
        --output=data/conserved/output/galGal3.amplicons.200-5000.bed

## run the intersection of these with refseq genes on UCSC (07/21/2010) and ##
## keep any results that cross a refseq gene at all.  Did this in the genome ##
## browser and pasted BED filed into galGal.refseq.200-5000.bed


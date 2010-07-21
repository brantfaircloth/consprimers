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
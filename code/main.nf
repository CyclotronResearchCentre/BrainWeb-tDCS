experimentCh = Channel
    .fromList( [
        ['MC', 'C3', 'C4'],
        ['MC', 'C3', 'Fp2'],
        ['dlPFC', 'F3', 'F4'],
        ['dlPFC', 'F3', 'Fp2'],
        ['vmPFC', 'F7', 'F8'],
        ['IPS', 'P3', 'P4']
    ] )
    .combine(
        Channel
            .fromPath( "${launchDir}/inputs/voi/results/brainweb-tdcs.db" )
    )
process extract_experiments_results {
    tag "roi: ${roi}, anode: ${anode}, cathode: ${cathode}"
    label 'duckdb'
    publishDir "${launchDir}/data/experiments", mode: 'copy'

    input:
    tuple roi, anode, cathode, file(db: "brainweb-tdcs.db") \
        from experimentCh

    output:
    tuple roi, anode, cathode, "roi-${roi}_anode-${anode}_cathode-${cathode}.csv" \
        into experimentCsvCh
    
    script:
    template 'extract_experiments_results.py'
}

roiCh = Channel
    .fromList( ['MC', 'dlPFC', 'vmPFC', 'IPS'] )
    .combine(
        Channel
            .fromPath( "${launchDir}/inputs/voi/results/brainweb-tdcs.db" )
    )
process extract_rois_results {
    tag "roi: ${roi}"
    label 'duckdb'
    publishDir "${launchDir}/data/rois", mode: 'copy'

    input:
    tuple roi, file(db: 'brainweb-tdcs.db') \
        from roiCh
    
    output:
    tuple roi, "roi-${roi}.csv" \
        into roiCsvCh
    
    script:
    template 'extract_rois_results.py'
}

notebookCh = Channel
    .fromPath( "${launchDir}/notebooks/*.ipynb" )
process convert_notebooks {
    tag "nb: ${notebook.baseName}"
    label 'python'
    publishDir "${launchDir}/results/html", mode: 'copy'

    input:
    path notebook \
        from notebookCh
    
    output:
    path "${notebook.baseName}.html" \
        into htmlNotebookCh
    
    shell:
    '''
    export BRAINWEB_TDCS_CODE_DIR="!{launchDir}/code"
    export BRAINWEB_TDCS_DATA_DIR="!{launchDir}/data"
    jupyter nbconvert !{notebook} --to notebook --execute
    jupyter nbconvert !{notebook.baseName}.nbconvert.ipynb --to html \
        --TagRemovePreprocessor.remove_cell_tags 'hide_cell' \
        --TagRemovePreprocessor.remove_input_tags 'hide_input' \
        --TagRemovePreprocessor.remove_all_outputs_tags 'hide_output' \
        --allow-chromium-download \
        --output !{notebook.baseName}
    '''
}
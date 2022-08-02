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

process generate_experiments_results {
    tag "roi: ${roi}, anode: ${anode}, cathode: ${cathode}"
    label 'python'
    publishDir "${launchDir}/data/experiments", mode: 'copy'

    input:
    tuple roi, anode, cathode, file(csv: "data.csv") \
        from experimentCsvCh
    
    output:
    tuple roi, anode, cathode, "roi-${roi}_anode-${anode}_cathode-${cathode}_gpr.csv" \
        into experimentGprCsvCh
    tuple roi, anode, cathode \
        into generatedFlagCh

    script:
    template 'generate_experiments_results.py'
}

generatedFlagCh.into { generatedFlagCh1; generatedFlagCh2; generatedFlagCh3 }

Channel
    .fromList(
        [
            ["MC", "C3", "C4", 0],
            ["MC", "C3", "Fp2", 1],
            ["dlPFC", "F3", "F4", 2],
            ["dlPFC", "F3", "Fp2", 3],
            ["vmPFC", "F7", "F8", 4],
            ["IPS", "P3", "P4", 5],
        ]
    ).into { experimentIdCh1; experimentIdCh2; experimentIdCh3; experimentIdCh4 }

anodePlacementNotebookCh = experimentIdCh1
    .combine(
        Channel.fromPath( "${launchDir}/notebooks/anode_placement.ipynb" )
    ).combine(
        Channel.from(0, 1)
    ).combine(
        generatedFlagCh1, by: [0, 1, 2]
    )
process convert_anode_placement_notebook {
    tag "roi: ${roi}, anode: ${anode}, cathode: ${cathode}"
    label 'python'
    publishDir "${launchDir}/results/html", mode: 'copy'

    input:
    tuple roi, anode, cathode, id, file(notebook: "anode_placement.ipynb"), use_gpr \
        from anodePlacementNotebookCh
    
    output:
    path "${notebook.baseName}_roi-${roi}_anode-${anode}_cathode-${cathode}${(use_gpr) ? '_gpr' : ''}.html" \
        into htmlAnodePlacementNotebookCh
    
    shell:
    '''
    export BRAINWEB_TDCS_CODE_DIR="!{launchDir}/code"
    export BRAINWEB_TDCS_DATA_DIR="!{launchDir}/data"
    export NOTEBOOK="!{notebook.baseName}_roi-!{roi}_anode-!{anode}_cathode-!{cathode}!{(use_gpr) ? '_gpr' : ''}.ipynb"
    papermill !{notebook} ${NOTEBOOK} -p experiment_id !{id} -p use_gpr !{use_gpr}
    jupyter nbconvert ${NOTEBOOK} --to html \
        --TagRemovePreprocessor.remove_cell_tags 'hide_cell' \
        --TagRemovePreprocessor.remove_cell_tags 'parameters' \
        --TagRemovePreprocessor.remove_cell_tags 'injected-parameters' \
        --TagRemovePreprocessor.remove_input_tags 'hide_input' \
        --TagRemovePreprocessor.remove_all_outputs_tags 'hide_output' \
        --allow-chromium-download
    '''
}

conductivityProfileNotebookCh = experimentIdCh2
    .combine(
        Channel.fromPath( "${launchDir}/notebooks/conductivity_profile.ipynb" )
    ).combine(
        Channel.from(0, 1)
    ).combine(
        generatedFlagCh2, by: [0, 1, 2]
    )
process convert_conductivity_profile_notebook {
    tag "roi: ${roi}, anode: ${anode}, cathode: ${cathode}"
    label 'python'
    publishDir "${launchDir}/results/html", mode: 'copy'

    input:
    tuple roi, anode, cathode, id, file(notebook: "conductivity_profile.ipynb"), use_gpr \
        from conductivityProfileNotebookCh
    
    output:
    path "${notebook.baseName}_roi-${roi}_anode-${anode}_cathode-${cathode}${(use_gpr) ? '_gpr' : ''}.html" \
        into htmlConductivityProfileNotebookCh
    
    shell:
    '''
    export BRAINWEB_TDCS_CODE_DIR="!{launchDir}/code"
    export BRAINWEB_TDCS_DATA_DIR="!{launchDir}/data"
    export NOTEBOOK="!{notebook.baseName}_roi-!{roi}_anode-!{anode}_cathode-!{cathode}!{(use_gpr) ? '_gpr' : ''}.ipynb"
    papermill !{notebook} ${NOTEBOOK} -p experiment_id !{id} -p use_gpr !{use_gpr}
    jupyter nbconvert ${NOTEBOOK} --to html \
        --TagRemovePreprocessor.remove_cell_tags 'hide_cell' \
        --TagRemovePreprocessor.remove_cell_tags 'parameters' \
        --TagRemovePreprocessor.remove_cell_tags 'injected-parameters' \
        --TagRemovePreprocessor.remove_input_tags 'hide_input' \
        --TagRemovePreprocessor.remove_all_outputs_tags 'hide_output' \
        --allow-chromium-download
    '''
}

bipolarUnipolarNotebookCh = Channel
    .fromList([
        ["MC", 0],
        ["dlPFC", 1]
    ]).combine(
        Channel.fromPath( "${launchDir}/notebooks/bipolar_unipolar.ipynb" )
    ).combine(
        Channel.from(0, 1)
    ).combine(
        generatedFlagCh3.groupTuple(by: 0), by: 0
    ).map { it -> tuple(it[0], it[1], it[2], it[3], it[4][0], it[4][1], it[5][0], it[5][1]) }
process convert_bipolar_unipolar_notebook {
    tag "roi: ${roi}"
    label 'python'
    publishDir "${launchDir}/results/html", mode: 'copy'

    input:
    tuple roi, id, file(notebook: "bipolar_unipolar.ipynb"), use_gpr, a1, a2, c1, c2 \
        from bipolarUnipolarNotebookCh
    
    output:
    path "${notebook.baseName}_roi-${roi}${(use_gpr) ? '_gpr' : ''}.html" \
        into htmlBipolarUnipolarNotebookCh
    
    shell:
    '''
    export BRAINWEB_TDCS_CODE_DIR="!{launchDir}/code"
    export BRAINWEB_TDCS_DATA_DIR="!{launchDir}/data"
    export NOTEBOOK="!{notebook.baseName}_roi-!{roi}!{(use_gpr) ? '_gpr' : ''}.ipynb"
    papermill !{notebook} ${NOTEBOOK} -p roi_id !{id} -p use_gpr !{use_gpr}
    jupyter nbconvert ${NOTEBOOK} --to html \
        --TagRemovePreprocessor.remove_cell_tags 'hide_cell' \
        --TagRemovePreprocessor.remove_cell_tags 'parameters' \
        --TagRemovePreprocessor.remove_cell_tags 'injected-parameters' \
        --TagRemovePreprocessor.remove_input_tags 'hide_input' \
        --TagRemovePreprocessor.remove_all_outputs_tags 'hide_output' \
        --allow-chromium-download
    '''
}

inducedPotentialNotebookCh = Channel
    .fromPath( "${launchDir}/notebooks/induced_transmembrane_potential.ipynb" )
    .combine(
        experimentIdCh3
    )
    .combine(
        Channel.from(0, 1)
    )
process convert_induced_transmembrane_potential_notebook {
    tag "roi: ${roi}, anode: ${anode}, cathode: ${cathode}"
    label 'python'
    publishDir "${launchDir}/results/html", mode: 'copy'

    input:
    tuple file(notebook: "induced_transmembrane_potential.ipynb"), roi, anode, cathode, id, use_gpr \
        from inducedPotentialNotebookCh
    
    output:
    path "${notebook.baseName}_roi-${roi}_anode-${anode}_cathode-${cathode}.html" \
        into htmlInducedPotentialNotebookCh
    
    shell:
    '''
    export BRAINWEB_TDCS_CODE_DIR="!{launchDir}/code"
    export BRAINWEB_TDCS_DATA_DIR="!{launchDir}/data"
    export NOTEBOOK="!{notebook.baseName}_roi-!{roi}_anode-!{anode}_cathode-!{cathode}!{(use_gpr) ? '_gpr' : ''}.ipynb"
    papermill !{notebook} ${NOTEBOOK} -p experiment_id !{id} -p use_gpr !{use_gpr}
    jupyter nbconvert ${NOTEBOOK} --to html \
        --TagRemovePreprocessor.remove_cell_tags 'hide_cell' \
        --TagRemovePreprocessor.remove_cell_tags 'parameters' \
        --TagRemovePreprocessor.remove_cell_tags 'injected-parameters' \
        --TagRemovePreprocessor.remove_input_tags 'hide_input' \
        --TagRemovePreprocessor.remove_all_outputs_tags 'hide_output' \
        --allow-chromium-download
    '''
}

/*subjectNotebookCh = Channel
    .fromPath( "${launchDir}/notebooks/subject.ipynb" )
    .combine(
        experimentIdCh4
    )
process convert_subject_notebook {
    tag "roi: ${roi}, anode: ${anode}, cathode: ${cathode}"
    label 'python'
    publishDir "${launchDir}/results/html", mode: 'copy'

    input:
    tuple file(notebook: "subject.ipynb"), roi, anode, cathode, id \
        from subjectNotebookCh
    
    output:
    path "${notebook.baseName}_roi-${roi}_anode-${anode}_cathode-${cathode}.html" \
        into htmlSubjectNotebookCh
    
    shell:
    '''
    export BRAINWEB_TDCS_CODE_DIR="!{launchDir}/code"
    export BRAINWEB_TDCS_DATA_DIR="!{launchDir}/data"
    export NOTEBOOK="!{notebook.baseName}_roi-!{roi}_anode-!{anode}_cathode-!{cathode}.ipynb"
    papermill !{notebook} ${NOTEBOOK} -p experiment_id !{id}
    jupyter nbconvert ${NOTEBOOK} --to html \
        --TagRemovePreprocessor.remove_cell_tags 'hide_cell' \
        --TagRemovePreprocessor.remove_cell_tags 'parameters' \
        --TagRemovePreprocessor.remove_cell_tags 'injected-parameters' \
        --TagRemovePreprocessor.remove_input_tags 'hide_input' \
        --TagRemovePreprocessor.remove_all_outputs_tags 'hide_output' \
        --allow-chromium-download
    '''
}*/
let selectedTemplate = null;
let blocksByPage = {};
let currentPage = 1;

$(document).ready(function() {
    loadBlocks();
    loadTemplates();

    $('#selected_template').on('click', function() {
        $('#templateDropdown').toggleClass('hidden'); // Ajoute/retire la classe 'hidden' pour afficher/masquer le dropdown
    });

    // Pour fermer le dropdown si on clique en dehors
    $(document).on('click', function(event) {
        if (!$(event.target).closest('#selected_template, #templateDropdown').length) {
            $('#templateDropdown').addClass('hidden');
        }
    });

    // si on clique sur un item du dropdown, on le sélectionne
    $('#templateDropdown').on('click', '.template-item', function() {
        select_template($(this).data('id_template'), $(this).text());
    });

    $('#prev-page').on('click', function() {
        if (currentPage > 1) {
            currentPage--;
            displayBlocksForPage(currentPage);
        }
    });

    $('#next-page').on('click', function() {
        if (currentPage < Object.keys(blocksByPage).length) {
            currentPage++;
            displayBlocksForPage(currentPage);
        }
    });
});

function loadBlocks() {
    $.ajax({
        url: '/reporting/create_reporting/get_blocks/',
        type: 'GET',
        success: function(response) {
            const blocks = response.data;

            blocks.forEach(block => {
                let width = block.position_x_end - block.position_x_start;
                let height = block.position_y_end - block.position_y_start;

                let blockItem = $('<div></div>', {
                    class: 'block-item bg-gray-100 border border-gray-300 rounded shadow p-2 mb-3 cursor-pointer text-center',
                    text: block.nom_block,
                    data: {
                        nom: block.nom_block,
                        description: block.description_block,
                        width: width,
                        height: height
                    }
                });

                blockItem.on('click', function() {
                    let newBlock = createDraggableBlock(
                        $(this).data('nom'),
                        $(this).data('description'),
                        $(this).data('width'),
                        $(this).data('height')
                    );
                    $('#a4-container').append(newBlock);
                });

                $('#blocks-container').append(blockItem);
            });
        },
        error: function(error) {
            console.error("Erreur lors du chargement des blocs : ", error);
        }
    });
}

function loadTemplates(){
    $.ajax({
        url: '/reporting/create_reporting/get_templates/',
        type: 'GET',
        success: function(response) {
            console.log("Templates : ", response.data);
            if (response.data && response.data.length > 0) {
                $('#template_list').empty();

                response.data.forEach(function(item){
                    $('#template_list').append(
                        `<div class="template-item cursor-pointer p-2 hover:bg-gray-200 text-left" data-id_template="${item.id_template}" onclick="select_template('${item.id_template}', '${item.nom_template}')">
                            ${item.nom_template}
                        </div>`
                    );
                });
            }
        },
        error: function(error) {
            console.error("Erreur lors du chargement des templates : ", error);
        }
    });
}

function select_template(id_template, nom_template){
    selectedTemplate = id_template;

    $('#selected_template').val(nom_template);
    fill_blocks();
}

function fill_blocks() {
    if (selectedTemplate) {
        $.ajax({
            url: '/reporting/create_reporting/get_blocks_template/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ id_template: selectedTemplate }),
            success: function(response) {
                if (response.data && response.data.length > 0) {
                    // Grouper les blocs par page
                    blocksByPage = {};
                    response.data.forEach(function(item) {
                        const pageNum = item.num_page || 1;
                        if (!blocksByPage[pageNum]) {
                            blocksByPage[pageNum] = [];
                        }
                        blocksByPage[pageNum].push(item);
                    });

                    currentPage = 1;
                    displayBlocksForPage(currentPage);
                }
            },
            error: function(error) {
                console.error("Erreur lors du chargement des blocs du template : ", error);
            }
        });
    }
}


function displayBlocksForPage(page) {
    $('#a4-container').empty();
    $('#current-page').text(`Page ${page}`);

    if (blocksByPage[page]) {
        blocksByPage[page].forEach(function(item) {
            let width = item.position_x_end - item.position_x_start;
            let height = item.position_y_end - item.position_y_start;
            let newBlock = createDraggableBlock(
                item.nom_block,
                item.description_block,
                width,
                height,
                item.position_x_start,
                item.position_y_start
            );

            $('#a4-container').append(newBlock);
        });
    }

    // Mettre à jour les boutons de pagination
    $('#prev-page').prop('disabled', page === 1);
    $('#next-page').prop('disabled', page === Object.keys(blocksByPage).length);
}


function createDraggableBlock(nom, description, width, height, posX, posY) {
    const maxX = 1040;
    const maxY = 1470;

    const containerWidth = $('#a4-container').width();
    const containerHeight = $('#a4-container').height();
    const scaleX = containerWidth / maxX;
    const scaleY = containerHeight / maxY;

    let adjustedWidth = width * scaleX;
    let adjustedHeight = height * scaleY;
    let adjustedPosX = posX * scaleX;
    let adjustedPosY = posY * scaleY;

    let block = $('<div></div>', {
        class: 'draggable-block bg-gray-100 border border-gray-300 rounded shadow p-2 absolute',
        text: nom,
        title: description,
        css: {
            width: adjustedWidth + 'px',
            height: adjustedHeight + 'px',
            top: adjustedPosY + 'px',
            left: adjustedPosX + 'px',
            position: 'absolute'
        }
    });

    block.draggable({
        containment: "#a4-container",
        scroll: false
    }).resizable({
        containment: "#a4-container"
    });

    block.on('dblclick', function() {
        $(this).remove();
    });

    return block;
}
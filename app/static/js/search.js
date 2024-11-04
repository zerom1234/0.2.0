$(document).ready(function() {
    $('#search').on('input', function() {
        const query = $(this).val();

        if (query.length > 2) {
            $.ajax({
                url: '/search',
                type: 'GET',
                data: { query: query },
                success: function(data) {
                    console.log(data)
                    const resultsList = $('#results');
                    resultsList.empty(); 

                    data.forEach(item => {
                        // Effacer les résultats si moins de 3 caractères mettre ici contruction de carte
                        const id_module = item.entity_id;
                        const entity_creation_time = item.entity_creation_time;
                        const entity_description_module = item.entity_description_module;
                        const entity_id_category = item.entity_id_category;
                        const entity_id_image_module = item.entity_id_image_module;
                        const entity_name_module = item.entity_name_module;
                        const entity_prix = item.entity_prix;
                        const image_id = item.image_id;
                        const image_image_filename = item.image_image_filename;
                        const image_image_original_name = item.image_image_original_name;
                        const image_upload_time = item.image_upload_time;

                        const li = $('<li></li>').text(image_image_filename);
                        resultsList.append(li);
                    });
                },
                error: function() {
                    console.error('Une erreur s\'est produite lors de la recherche.');
                }
            });
        } else {
            // Effacer les résultats si moins de 3 caractères
            $('#results').empty();
        }
    });
});
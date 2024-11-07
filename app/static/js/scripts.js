$(document).ready(function() {
    console.log('JavaScript is loaded'); // Verificar que JavaScript se está cargando

    // Abrir el modal cuando se haga clic en el botón que abre el modal
    $('#calculateTokensButton').on('click', function() {
        console.log('Opening Token Calculator Modal');
        $('#tokenCalculatorModal').modal('show');
    });

    // Registrar el evento de click del botón de calcular tokens cuando el modal se muestra
    $('#tokenCalculatorModal').on('shown.bs.modal', function() {
        console.log('Token Calculator Modal is now shown');

        // El botón de calcular tokens dentro del modal
        $('#calculateTokensButtonModal').off('click').on('click', function() {
            console.log('Calculate Tokens button clicked inside modal');

            // Obtener el valor del campo de texto
            const exampleText = $('#exampleText').val().trim();
            const selectedModel = $('#modelSelection').val(); // Obtener el modelo seleccionado
            console.log('Text in #exampleText:', exampleText); // Mostrar el valor del campo de texto
            console.log('Model selected:', selectedModel); // Mostrar el modelo seleccionado

            if (exampleText.length > 0) {
                console.log('Text to calculate tokens:', exampleText); // Mostrar el texto que se va a enviar

                // Realizar una solicitud AJAX al backend para calcular tokens
                $.ajax({
                    url: '/calculate_tokens',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ text: exampleText, model: selectedModel }),
                    success: function(response) {
                        console.log('Tokens calculated:', response.tokens); // Mostrar la respuesta
                        $('#calculatedTokens').val(response.tokens);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error calculating tokens:', status, error); // Mostrar el error en consola
                        console.error('Full response:', xhr.responseText); // Mostrar la respuesta completa
                        alert('Error calculating tokens. Please try again.');
                    }
                });
            } else {
                console.log('No text provided'); // Verificar si no hay texto
                alert('Please enter some text to calculate the tokens.');
            }
        });
    });

    // Actualizar el valor del campo "tokens_per_interaction" al cerrar el modal
    $('#closeModalButton').on('click', function() {
        const calculatedTokens = $('#calculatedTokens').val();
        if (calculatedTokens) {
            $('#tokens_per_interaction').val(calculatedTokens);
        }
    });
});

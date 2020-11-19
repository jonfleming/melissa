const csrftoken = Cookies.get('csrftoken');

function csrfSafeMethod(method) {
// these HTTP methods do not require CSRF protection
return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
    });

    const $chatlog = $('.js-chat-log');
    const $input = $('.js-text');
    const $sayButton = $('.js-say');

    function createRow(text) {
        const $row = $('<li class="list-group-item"></li>');

        $row.text(text);
        $chatlog.append($row);
    }

    function submitInput() {
        const inputData = { 'text': $input.val() };

        // Display the user's input on the web page
        createRow(inputData.text);

        $.ajax({
            type: 'POST',
            url: chatterbotUrl,
            data: JSON.stringify(inputData),
            contentType: 'application/json'
        }).done(function(statement) {
            createRow(statement.text);
            sayText(statement.text,2,1,3);
            // Clear the input field
            $input.val('');

            // Scroll to the bottom of the chat interface
            $chatlog[0].scrollTop = $chatlog[0].scrollHeight;
        }).fail(function(jdXHR, textStatus) {
            // TODO: Handle errors
            alert('ajax request failed');
        });
    }

    $sayButton.click(function() {
        submitInput();
    });

    $input.keydown(function(event) {
    // Submit the input when the enter button is pressed
    if (event.keyCode == 13) {
        submitInput();
    }
});

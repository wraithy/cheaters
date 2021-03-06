
$(document).ready(function(){
    // redirects click event of button to input type file
    $("#id_fake_file_button").click(
        function () {
            $("#id_file").click();

        }
    )

    // updates the filename label when a file has been chosen
    $( "#id_file" ).on( "change", function updateFileName( event ){
       var input = $( this );
       var label = input.val().replace(/([^\\]*\\)*/,'');
       $("#id_file_name").html("\</br\>\</br\>\</br\>\<b\>"+label+"\</b\>");
       });
});


//Callback handler for form submit event
$(document).ready(function(){
    $("#uploadform").submit(function(e)
    {
        $("ul[name=error_message]").remove();
        var formObj = $(this);
        var formURL = formObj.attr("action");
        var formData = new FormData(this);
        $.ajax({
            url: formURL,
            type: 'POST',
            data:  formData,
            mimeType:"multipart/form-data",
            contentType: false,
            cache: false,
            processData:false,
        success: function(response)
        {
            var report_id = $.parseJSON(response).report_id
            window.location = "/report/"+report_id
        },

        error: function(response)
        {
            console.log(response)
            $.each($.parseJSON(response.responseText), function(element, error){
                var ul = $("<ul>").attr({name: "error_message", class: "form-error-message"});
                ul.text(element + ": " + error);

                $("#error_messages").append(ul);

            });


        }
        });
        e.preventDefault(); //Prevent Default action.

    });
});
$("#uploadform").submit(); //Submit the form

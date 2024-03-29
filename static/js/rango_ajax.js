$('#likes').click(function() {
    const catid = $(this).attr('data-catid');
    $.get('/rango/like/', 
        {category_id: catid},
        function(data) {
            $('#like_count').html(data);
            $('#likes').hide();
        }
    );
});

$('#suggestion').keyup(function() {
    const query = $(this).val();
    $.get('/rango/suggest/', 
        {suggestion: query},
        function(data) {
            $('#cats').html(data);
        }
    );
});

$('#search-profile').keyup(function() {
    const query = $(this).val()
    $.get('/rango/search_profile/',
        { search: query },
        function(data) {
            $('#list-profiles').html(data)
        }
    )
})

$('.rango-add').click(function() {
    const catid = $(this).attr("data-catid");
    const url = $(this).attr("data-url");
    const title = $(this).attr("data-title");
    const me = $(this);
    $.get('/rango/add/',
        {
            category_id: catid,
            url: url,
            title: title,
        },
        function(data) {
            $('#pages').html(data);
            me.hide();
        })
})

$('#dark-mode').change(function() {
    console.log('henlo')
    console.log($(this).is(':checked'))
    $.get('/rango/update_settings/',
        {
            darkmode: $(this).is(':checked')
        },
        function(data) {
            // $.cookie('dark_mode', false)
            $('.henlo').html(data)
        }
    )
});

// $('#dark-mode').click(function() {
//     $.ajax({
//         type: 'POST',
//         url: '/rango/settings/',
//         data: {
//             dark_mode: $('#dark-mode').val()
//         },
//         success: function() {

//         }
//     })
// });

$('#login_form, #registration_form')
    .children('p')
    .children(`input[type*='text'], input[type*='password'], input[type*='email']`)
    .addClass('form-control');

$('#category_form, #add_page_form')
    .children(`input[type*='text'], input[type*='url']`)
    .addClass('form-control my-3');

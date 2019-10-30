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

$('#login_form, #registration_form')
    .children('p')
    .children(`input[type*='text'], input[type*='password'], input[type*='email']`)
    .addClass('form-control');

$('#category_form, #add_page_form')
    .children(`input[type*='text'], input[type*='url']`)
    .addClass('form-control my-3');

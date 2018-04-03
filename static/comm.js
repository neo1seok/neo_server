function show_input_enable(is_enable){
    console.log('show_input_enable',is_enable);
    if(is_enable){
        $('.neo_form').removeAttr('disabled');
    }
    else{
        $('.neo_form').attr('disabled', '');
    }

}
function temp_query(url,data,ok_process,err_process=function(err) {console.log(error);}){
    $.ajax({
        url: url,
        data: data,
        type: 'POST',
        dataType: "json",
        success: function(response) {
            if(response.result == "OK"){
                ok_process(response);

            }
            console.log(response);

        },
        error: err_process
    });

}
function confirm(url){
    console.log("btn_confirm",$('#form_input').serializeArray());



    temp_query(url,$('form').serializeArray(),function(response){
        console.log("confirm ok aaaa");
        location.reload();
    })
//
//     $.ajax({
//        url: url,
//        data: $('form').serializeArray(),
//        type: 'POST',
//        dataType: "json",
//        success: function(response) {
//            if(response.result == "OK"){
//               location.reload();
//            }
//            console.log(response);
//
//        },
//        error: function(error) {
//            console.log(error);
//        }
//    });
}

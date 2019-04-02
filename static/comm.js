function show_input_enable(input_class,is_enable){
    console.log('show_input_enable',is_enable);
    var obj = $('.'+input_class )
    if(is_enable){
        obj.removeAttr('disabled');
    }
    else{
        obj.attr('disabled', '');
    }
    return is_enable;

}
function temp_query(url,data,ok_process,err_process=function(error) {
                alert(error);
                console.log(error);
            }){
    $.ajax({
        url: url,
        data: data,
        type: 'POST',
        dataType: "json",
        success: function(response) {
            if(response.result == "ok"){
                ok_process(response);
                return;

            }

            console.log(response);
            err_process(response.error);

        },
        error: err_process
    });

}
function confirm_form(url,reload_url){
    console.log("btn_confirm",$('#form_input').serializeArray());



    temp_query(url,$('form').serializeArray(),function(response){
        console.log("confirm ok aaaa");
        location = reload_url ;
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

function sha256_from_hexstr(hex_str){
  var str = hex2a(hex_str);
  console.log(str);

  //
  return Sha256.hash(hex_str,{ msgFormat: 'hex-bytes', outFormat: 'hex' });
	//return crypto_util.sha256(neoutil.Text2HexString(passwd) + rn)
}


function toHex(str) {
  var result = '';
  for (var i = 0; i < str.length; i++) {
    result += str.charCodeAt(i).toString(16);
  }

  return result.toUpperCase();
}

function hex2a(hexx) {
  var hex = hexx.toString(); //force conversion
  var str = '';
  for (var i = 0; i < hex.length; i += 2)
    str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
  return str;
}

function reset_message(){
console.log('reset_message');
$('#id_alert').hide();
$('#id_warning').hide();
$('#id_alert > strong').text('');
$('#id_warning > strong').text('');

}

function show_message(id,msg){
$('#'+id ).show();
$('#'+id +" > strong").text(msg);
}

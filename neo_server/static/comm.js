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
        //location = reload_url ;
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

function setCookie(cookie_name, value, days) {
  var exdate = new Date();
  exdate.setDate(exdate.getDate() + days);
  // 설정 일수만큼 현재시간에 만료값으로 지정

  var cookie_value = escape(value) + ((days == null) ? '' : ';    expires=' + exdate.toUTCString());
  document.cookie = cookie_name + '=' + cookie_value;
}

function getCookie(cookie_name) {
  var x, y;
  var val = document.cookie.split(';');

  for (var i = 0; i < val.length; i++) {
    x = val[i].substr(0, val[i].indexOf('='));
    y = val[i].substr(val[i].indexOf('=') + 1);
    x = x.replace(/^\s+|\s+$/g, ''); // 앞과 뒤의 공백 제거하기
    if (x == cookie_name) {
      return unescape(y); // unescape로 디코딩 후 값 리턴
    }
  }
}
function addCookie(id) {
  var items = getCookie('productItems'); // 이미 저장된 값을 쿠키에서 가져오기
  var maxItemNum = 5; // 최대 저장 가능한 아이템개수
  var expire = 7; // 쿠키값을 저장할 기간
  if (items) {
    var itemArray = items.split(',');
    if (itemArray.indexOf(id) != -1) {
      // 이미 존재하는 경우 종료
      console.log('Already exists.');
    }
    else {
      // 새로운 값 저장 및 최대 개수 유지하기
      itemArray.unshift(id);
      if (itemArray.length > maxItemNum ) itemArray.length = 5;
      items = itemArray.join(',');
      setCookie('productItems', items, expire);
    }
  }
  else {
    // 신규 id값 저장하기
    setCookie('productItems', id, expire);
  }
}



function copy_clipboard_from_input_id(input_id) {
  /* Get the text field */
  //var copyText = document.getElementById("myInput");
  var copyText = $('#'+input_id);

  /* Select the text field */
  //copyText.select();
  copyText.select();


  /* Copy the text inside the text field */
  document.execCommand("copy");

  /* Alert the copied text */
  //alert("Copied the text: " + copyText2.val());
}


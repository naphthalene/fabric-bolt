$(function(){
  if(deployment_in_progress){

    var socket = io.connect("/deployment");

    socket.on('connect', function () {
      socket.emit('join', deployment_id);
      if(data.status == 'running' && typeof(deployment_text) != "undefined"){
        $('#deployment_output pre').append(deployment_text).scrollTop($('#deployment_output pre')[0].scrollHeight);
      }
    });

    socket.on('output', function (data) {
      console.log("Task is " + data.status)
      if(data.status == 'running' || data.status == 'pending'){
        $('#deployment_output pre').append(data.lines).scrollTop($('#deployment_output pre')[0].scrollHeight);
      }else{
        socket.disconnect();
        if(data.status == 'failed'){
          $('#status_section legend').html('Status: Failed!');
          $('#status_section .glyphicon').attr('class', '').addClass('glyphicon').addClass('glyphicon-remove').addClass('text-danger');
        }else if(data.status == 'success') {
          $('#status_section legend').html('Status: Success!');
          $('#status_section .glyphicon').attr('class', '').addClass('glyphicon').addClass('glyphicon-ok').addClass('text-success');
        }else if(data.status == 'aborted') {
          $('#status_section legend').html('Status: Aborted!');
          $('#deployment_abort').hide();
          $('#status_section .glyphicon').attr('class', '').addClass('glyphicon').addClass('glyphicon-warning-sign').addClass('text-warning');
        }
      }

    });

    $('#deployment_input').keyup(function(e){
      if(e.which == 13){
        var text = $(this).val();
        $(this).val('');
        socket.emit('input', {
          'type' : 'text',
          'text' : text
        });
        $('#deployment_output pre').append('\n');
      }
    });

    $('#deployment_abort').click(function(){
      socket.emit('input', {
        'type' : 'abort',
        'pk' : deployment_id
      });
    });

    $("#deployment_maximize").click(function(){

      var clone = $('#deployment_well').clone().addClass('active');
      var parent = $('#deployment_well').parent();
      var pos = $('#deployment_well').position();

      $('body').append(clone);
      clone.focus()

      clone.css({'position' : 'absolute', left: pos.left + 'px', top: pos.top + 'px'}).animate({
        width: '100%', height : '100%', top: 0, left: 0
      },300);
    });

  }else{
    $('#deployment_output pre').scrollTop($('#deployment_output pre')[0].scrollHeight);
  }
});

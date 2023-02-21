$(document).ready(function(){
    $.ajax({
      type: 'GET',
      url: '/votes',
      success: function(response){
        var likes = response['likes']
        var dislikes = response['dislikes']
        
        for (let post_id in likes[0] ){
          $("#likes_"+post_id).text(likes[0][post_id])
          if (likes[1][post_id]){
            $("#green_"+post_id).css("color","#5f788a")
            $("#red_"+post_id).css("color","#AAA")
          }else{
            $("#green_"+post_id).css("color","#AAA")
          }
        }

        for (let post_id in dislikes[0] ){
          $("#dislikes_"+post_id).text(dislikes[0][post_id])
          if (dislikes[1][post_id]){
            $("#red_"+post_id).css("color","#5f788a")
            $("#green_"+post_id).css("color","#AAA")
          }else{
            $("#red_"+post_id).css("color","#AAA")
          }
        }
      }
    })
    
    $(".btn_like").click(function(e){
    e.preventDefault();

    var id = this.id;
    var split_id = id.split("_")
    var post_id = split_id[1]
    
    $.ajax({
      type: 'POST',
      url: '/vote/like',
      data: {
        post_id: post_id
      },
      success: function(data){
        var likes = data['likes']
        var dislikes = data['dislikes']

        $("#likes_"+post_id).text(likes[0][post_id])
        $("#dislikes_"+post_id).text(dislikes[0][post_id])

        if (likes[1][post_id]){
          $("#green_"+post_id).css("color","#5f788a")
          $("#red_"+post_id).css("color","#AAA")
        }else{
          $("#green_"+post_id).css("color","#AAA")
        }
      }
    })

    $(".btn_dislike").click(function(e){
    e.preventDefault();

    var id = this.id;
    var split_id = id.split("_")
    var post_id = split_id[1]
    
    $.ajax({
      type: 'POST',
      url: '/vote/dislike',
      data: {
        post_id: post_id
      },
      success: function(data){
        var likes = data['likes']
        var dislikes = data['dislikes']
        
        $("#likes_"+post_id).text(likes[0][post_id])
        $("#dislikes_"+post_id).text(dislikes[0][post_id])

        if (dislikes[1][post_id]){
          $("#red_"+post_id).css("color","#5f788a")
          $("#green_"+post_id).css("color","#AAA")
        }else{
          $("#red_"+post_id).css("color","#AAA")
        }
      }
    })
  })
  })})
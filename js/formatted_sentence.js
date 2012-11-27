var training = d3.select('#formatted_question');


// Returns a URL property by name, stolen wholesale of AWS docs
function gup( name )
{
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  var tmpURL = window.location.href;
  var results = regex.exec( tmpURL );
  if( results == null )
    return "";
  else
    return results[1];
}

// Generate questions
d3.json('../data/training_no_answers.json', function(data) {

    // Get question passed by qualification test
    var tuid = gup("text_unit_id"),
    	questions = data.filter(function(d) {
    		return (d["text_unit_id"] == tuid)
    	}),
    	question_num = gup("question_num");

    console.log(question_num)

    if(questions.length < 1 | question_num == "") {
        training.append("div")
            .attr("class", "row")
            .append("div")
                .attr("class", "span12")
                .append("h2")
                    .attr("class", "text-error")
                    .text("Invalid 'text_unit_id', something has gone wrong!")
    }
    else {
        questions.forEach(function(d, i) {
            // Create containers for questions and buttons
            var q = training.append("div")
                        .attr("class", "row")
                        .attr("id", "question_"+question_num),

                // Attach question text
                q_div = q.append("div")
                        .attr("class", "span12"),

                // num = q_div.append("h4")
                //         .text("#" + (i+1)),

                q_text = q_div.append("div")
                        .attr("class", "manifesto_text")
                        .attr("name", "text_unit_id")
                        .attr("value", d["text_unit_id"]),
                        

                pre_text = q_text.append("div")
                        .attr("class", "context_text")
                        .text(d["pre_sentence"]),

                code_text = q_text.append("div")
                        .attr("class", "code_text")
                        .text(d["sentence_text"]),

                post_text = q_text.append("div")
                        .attr("class", "context_text")
                        .text(d["post_sentence"]);
    	});
    }
});
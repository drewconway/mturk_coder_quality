var econ_scale = [{'label':'', 'value':'NA'},
                    {'label':'Very left', 'value':-2}, 
                    {'label':'Somewhat left', 'value':-1}, 
                    {'label':'Neither left nor right', 'value':0}, 
                    {'label':'Somewhat right', 'value':1}, 
                    {'label':'Very right', 'value':2}],
    
    soc_scale = [{'label':'', 'value':'NA'},
                    {'label':'Very liberal', 'value':-2}, 
                    {'label':'Somewhat liberal', 'value':-1}, 
                    {'label':'Neither liberal nor conservative', 'value':0}, 
                    {'label':'Somewhat conservative', 'value':1}, 
                    {'label':'Very conservative', 'value':2}],

    prod = gup("prod"),
    hit_type = gup("type");

    num_questions = gup("n");
    if(num_questions == "") {
        num_questions = 1
    }
    if(parseInt(num_questions) > 10) {
        num_questions = 10;
    }

    if(prod == "y") {
        var training = d3.select('#hit')
        .append("form")
            .attr("method", "GET")
            .attr("action", "http://www.mturk.com/mturk/externalSubmit")
            .attr("id", "hit_form");
    }
    else {
        var training = d3.select('#hit')
        .append("form")
            .attr("method", "GET")
            .attr("action", "http://workersandbox.mturk.com/mturk/externalSubmit")
            .attr("id", "hit_form");
    }

    var assignment_id = training.append("input")
            .attr("type", "hidden")
            .attr("id", "assignmentId")
            .attr("name", "assignmentId")
            .attr("value", "");


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

function checkPreview() {
    var current_assignment_id = gup("assignmentId");
    if(current_assignment_id == "ASSIGNMENT_ID_NOT_AVAILABLE") {
        var submit_btn = d3.select("#codings-btn")
                .text("This is only a preview. You must ACCEPT the HIT before you can submit the results."),

            instructions = d3.select("#instructionsCollapse")
                .attr("class", "accordion-body");
    }
    else {
        assignment_id.attr("value", current_assignment_id);
        validateCodings();
    }
}

// Return N values from a sample array, with or without
// replacement.
function sample_range(range, n, replacement) {
    var sample = [];
    if(!replacement) {
        var values = [];
    }
    for(var i=0; i<n; i++) {
        var x = Math.floor(Math.random()*range.length);
        if(!replacement) {
            while(sample.indexOf(x) > -1) {
                var x = Math.floor(Math.random()*range.length);
            }
            values.push(x)
        }
        sample.push(range[x])
    }
    return sample;
}

function validateCodings() {
    // Check that all sentences have some policy area
    // coding. If so, enable submission button.
    var area_selections = d3.selectAll(".area_select"),
        submit_btn = d3.select("#codings-btn"),
    
    area_values = area_selections[0].map(function(d) { return d.value; });
    
    // Check if they all have some policy area value
    if(area_values.filter(function(d) { return (d=="0"); }).length > 0) {
        submit_btn.attr("disabled", "disabled")
            .text("Task incomplete");
    }
    else {
        submit_btn.attr("disabled", null)
            .text("Submit codings");
    }
}

function areaSelect (area_value, area_num) {
    // Collect focus select element
    var scale_select = d3.select("#scale_"+area_num),
        label_select = d3.select("#scale_label_"+area_num);

    // Clean things up if user changes mind
    scale_select.selectAll("option").remove();
    label_select.selectAll("p").remove();

    
    if(area_value == 0) {
        var policy_scale = scale_select.append("option")
                .attr("value", "NA")
                .attr("label", "")
                .text(""),

            scale_warning = label_select.append("p")
                .attr("class", "text-error pull-right")
                .text("You must select a policy area!");         
    }
    if(area_value == 1) {
        var policy_scale = scale_select.append("option")
                .attr("value", "NA")
                .attr("label", "")
                .text(""),

            scale_message = label_select.append("p")
                .attr("class", "muted pull-right")
                .text("No policy scale");

    }
    if(area_value == 2) {
        var policy_scale = scale_select.selectAll("option")
            .data(econ_scale)
          .enter()
            .append("option")
                .attr("value", function(d) { return d["value"]; })
                .attr("label", function(d) { return d["label"]; })
                .text(function(d) { return d["label"]; }),

            scale_message = label_select.append("p")
                .attr("class", "pull-right")
                .text("Select economic policy scale:");
    }
    if(area_value == 3) {
        var policy_scale = scale_select.selectAll("option")
            .data(soc_scale)
          .enter()
            .append("option")
                .attr("value", function(d) { return d["value"]; })
                .attr("label", function(d) { return d["label"]; })
                .text(function(d) { return d["label"]; }),

            scale_message = label_select.append("p")
                    .attr("class", "pull-right")
                    .text("Select social policy scale:");
    }
    validateCodings();
}

// Generate questions
d3.json('../data/experimental.json', function(data) {

    // Pick questions to be coded

    if(hit_type == "econ") {
        var type_data = data.filter(function(d) {
            return(d["policy_area_gold"] == "2" | d["policy_area_gold"] == "1");
        }),
        policy_area = [{'label':'Select policy area', 'value':0, 'text': 'Select one'},
                   {'label':'Economic', 'value':2, 'text': 'Economic'},
                   {'label':'Not Economic', 'value':1, 'text': 'Not Economic'}];
    }
    else {
        if(hit_type == "soc") {
            var type_data = data.filter(function(d) {
                return(d["policy_area_gold"] == "3" | d["policy_area_gold"] == "1");
            }),
            policy_area = [{'label':'Select policy area', 'value':0, 'text': 'Select one'},
                   {'label':'Social', 'value':3, 'text': 'Social'},
                   {'label':'Not Social', 'value':1, 'text': 'Not Social'}];
        }
        else {
            var type_data = data,
            policy_area = [{'label':'Select policy area', 'value':0, 'text': 'Select one'},
                   {'label':'Not Economic or Social', 'value':1, 'text': 'Not Economic or Social'},
                   {'label':'Economic', 'value':2, 'text': 'Economic'},
                   {'label':'Social', 'value':3, 'text': 'Social'}];
        }
    }

    // console.log(type_data.length)

    var questions = sample_range(type_data, num_questions, false),

    form_language = training.append("input")
        .attr("type", "hidden")
        .attr("id", "lang")
        .attr("name", "lang")
        .attr("value", navigator.language);

    if(questions.length < 1) {
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
                        .attr("id", "question_"+i),

                buttons = training.append("div")
                        .attr("class", "row")
                        .attr("id", "buttons_"+i),

                btn_area = buttons.append("div")
                        .attr("class", "span2 offset2"),

                scale_label = buttons.append("div")
                        .attr("class", "span3 offset1")
                        .attr("id", "scale_label_"+i),

                btn_scale = buttons.append("div")
                        .attr("class", "span2")
                        .attr("id", "q_text"+i),

                // Attach question text
                q_div = q.append("div")
                        .attr("class", "span12"),

                num = q_div.append("h4")
                        .text("#" + (i+1)),
                        

                q_text = q_div.append("div")
                        .attr("class", "manifesto_text"),

                q_text_id = q_div.append("input")
                        .attr("type", "hidden")
                        .attr("id", "text_unit_id_"+i)
                        .attr("name", "text_unit_id_"+i)
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

                // Attach policy area button
                area_select = btn_area.append("select")
                        .attr("class", "area_select")
                        .attr("id", "area_"+i)
                        .attr("name", "area_"+i)
                        .on("change", function() { areaSelect(this.value, i); }),

                area_options = area_select.selectAll("option")
                        .data(policy_area)
                      .enter()
                        .append("option")
                            .attr("value", function(d) { return d["value"]; })
                            .attr("label", function(d) { return d["label"]; })
                            .text(function(d) { return d["label"]; }),

                // Attach policy scale button
                scale_select = btn_scale.append("select")
                        .attr("id", "scale_"+i)
                        .attr("name", "scale_"+i),

                // Add separation line
                separator = training.append("div")
                    .attr("class", "row")
                    .append("div")
                        .attr("class", "span12")
                        .append("hr");
        });
        var form_action = training.append("div")
            .attr("class", "row form-actions"),

            form_heading = form_action.append("div")
                .attr("class", "span4")
                .append("h4")
                .text("Submit Coding"),

            form_buttons = form_action.append("div")
                .attr("class", "span12")
                .append("button")
                    .attr("type", "submit")
                    .attr("class", "btn btn-large btn-primary right-right")
                    .attr("id", "codings-btn")
                    .attr("disabled", "disabled")
                    .text("Task incomplete");                
        checkPreview();
    }
});
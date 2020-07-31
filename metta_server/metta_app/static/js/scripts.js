$(document).ready(function () {
  // Get tasks at page load
  get_and_generate_tasks();

  // Growth Period Input, creates entries in database
  $("#growth_period_button").click(function () {
    growth_period = parseInt(
      window.prompt(
        "Enter the estimated growth period (weeks) for the plant:",
        4
      )
    );
    $("#growth_weeks").text(growth_period + " weeks");

    $.ajax({
      type: "GET",
      url: "scheduler",
      data: { growth_period: growth_period },
      success: function (response) {
        get_and_generate_tasks();
        console.log(response);
      },
      error: function (response) {
        console.log(response);
      },
    });

    // $.ajax({
    //   type: "GET",
    //   url: "tray_state",
    //   data: {new: true},
    //   success: function (response) {
    //     set_tray_color('tray1', response.tray1);
    //     set_tray_color('tray2', response.tray2);
    //     set_tray_color('tray3', response.tray3);
    //     set_tray_color('tray4', response.tray4);
    //     console.log(response);
    //   },
    //   error: function (response) {
    //     console.log(response);
    //   },
    
    });

  // Nutrient Calculator
  $("#calculate").click(function () {
    var target_conc = parseFloat($("#target_conc").val());
    var water_vol = parseFloat($("#water_vol").val());

    $.ajax({
      type: "GET",
      url: "latest_sensor_val",
      data: { calc: true, target_conc: target_conc, water_vol: water_vol },
      success: function (response) {
        // console.log(response);
        output = parseFloat(response.nutr_vol).toFixed(1);
        $("#nutr_vol").text(output + " ml");
      },
      error: function (response) {
        console.log(response);
      },
    });
  });

  // Realtime EC/Temp Display + Tray States
  var continuous_call = function () {
    $.ajax({
      type: "GET",
      url: "latest_sensor_val",
      success: function (response) {
        // console.log(response);
        $("#temp_display").text(response.temp);
        $("#ec_display").text(response.ec);
      },
      error: function (response) {
        console.log(response);
      },
    });

    $.ajax({
      type: "GET",
      url: "tray_state",
      success: function (response) {
        set_tray_color("tray1", response.tray1);
        set_tray_color("tray2", response.tray2);
        set_tray_color("tray3", response.tray3);
        set_tray_color("tray4", response.tray4);
      },
      error: function (response) {
        console.log(response);
      },
    });
  };

  var interval = 3000; // 3 secs
  setInterval(continuous_call, interval);
});

/*
FUNCTIONS
*/

function color_to_hex(color) {
  switch (color) {
    case "red":
      return "#ff9798";
    case "orange":
      return "#FFDA83";
    case "blue":
      return "#b3e5fc";
    case "green":
      return "#BAEE8D";
    case "blank":
      return "#E8E9EC";
  }
}

function set_tray_color(tray_class, color) {
  color = color_to_hex(color);
  $("." + tray_class).css("background-color", color);
}


// Adds singular task card
function add_task(task, tray, color, first = false) {
  check1 = "hidden";
  arrow2 = "hidden";
  arrow3 = "hidden";
  check4 = "hidden";

  color = color_to_hex(color);

  if (task == "Transfer") {
    if (tray == 2) arrow2 = "";
    if (tray == 3) arrow3 = "";
  }

  if (task == "Harvest") {
    if (tray == 1) check1 = "";
    if (tray == 4) check4 = "";
  }

  html =
    '<div class="card shadow mb-4"> <div class="card-header py-3"> <h6 class="font-weight-bold m-0" style="font-family: Lato, sans-serif;font-size: 18px;">' +
    task +
    '</h6> </div> <div class="card-body"> <div class="row"> <div class="col"> <div class="text-uppercase text-info font-weight-bold text-xs mb-1"></div> </div> </div> <div class="row">';

  for (i = 1; i <= 4; i++) {
    html +=
      '<div class="col-lg-3"> <div class="card"> <div class="card-body" style="background-color: ';
    i == tray ? (html += color) : (html += "#E8E9EC");
    html += ';padding: 10px;height: 54px;"></div> </div> </div> ';
  }

  html += "</div> ";
  html +=
    '<div class="row" style="margin-bottom: 10px;margin-top: -44px;height: 34.8571px;"> ' +
    '<div class="col"> <div class="text-uppercase text-info font-weight-bold text-xs mb-1"> </div><i class="material-icons" ' +
    check1 +
    ">check</i></div> " +
    '<div class="col"> <div class="text-uppercase text-info font-weight-bold text-xs mb-1"></div><i class="material-icons" style="margin-left: -26px;" ' +
    arrow2 +
    ">arrow_back</i></div> " +
    '<div class="col"> <div class="text-uppercase text-info font-weight-bold text-xs mb-1"></div><i class="material-icons" style="margin-left: 80px;" ' +
    arrow3 +
    ">arrow_forward</i></div> " +
    '<div class="col"> <div class="text-uppercase text-info font-weight-bold text-xs mb-1"></div><i class="material-icons" ' +
    check4 +
    ">check</i></div> </div>";
  html += "</div>";
  html +=
    '<div class="card-footer"> <div class="row text-right"> <div class="col" style="height: 26.8571px"><span id="clear_task_button" style="font-family: Lato, sans-serif;font-size: 18px;">';
  first ? (html += "Clear") : (html += "");
  html += "</span></div> </div> </div> </div>";

  $("#task_col").append(html);
}

// delete old cards, get tasks from database, calls add_task to generate html for cards
function get_and_generate_tasks() {
  $("#task_col").empty();

  $.ajax({
    type: "GET",
    url: "scheduler",
    success: function (response) {
      console.log(response.data);
      for (let i = 0; i < response.data.length; i++) {
        e = response.data[i];
        let flag = i == 0 ? true : false;
        console.log(e);

        if (e.to_harvest != "blank") {
          if (e.to_harvest == "red" || e.to_harvest == "orange") {
            add_task("Harvest", 1, e.to_harvest, flag);
            flag = false;
          } else if (e.to_harvest == "blue" || e.to_harvest == "green") {
            add_task("Harvest", 4, e.to_harvest, flag);
            flag = false;
          }
        }
        if (e.to_transfer != "blank") {
          if (e.to_transfer == "red" || e.to_transfer == "orange") {
            add_task("Transfer", 2, e.to_transfer, flag);
            flag = false;
          } else if (e.to_transfer == "blue" || e.to_transfer == "green") {
            add_task("Transfer", 3, e.to_transfer, flag);
            flag = false;
          }
        }
        if (e.to_plant != "blank") {
          if (e.to_plant == "red" || e.to_plant == "orange") {
            add_task("Plant", 2, e.to_plant, flag);
            flag = false;
          }
          if (e.to_plant == "blue" || e.to_plant == "green") {
            add_task("Plant", 3, e.to_plant, flag);
            flag = false;
          }
        }
      }
      //enable task 'clear' button
      setTimeout(function () {
        $("#clear_task_button").click(function () {
          if (response.data[0].to_harvest != 'blank') { complete_task('harvest'); console.log('harvest clear')}
          else if (response.data[0].to_transfer != 'blank') { complete_task('transfer'); console.log('transfer clear')}
          else if (response.data[0].to_plant != 'blank') { complete_task('plant'); console.log('plant clear')}
        });
      }, 2);
    },
    error: function (response) {
      console.log(response);
    },
  });
}

//sets task as completed in database, calls get_and_generate_tasks() to recreate cards
function complete_task(task_type) {
  $.ajax({
    type: "GET",
    url: "scheduler",
    data: { completed: task_type },
    success: function (response) {
      // console.log(response);
      // output = parseFloat(response.nutr_vol).toFixed(1);
      // $("#nutr_vol").text(output + ' ml');
      get_and_generate_tasks();

      $.ajax({
        type: "GET",
        url: "tray_state",
        data: {task_done: true},
        success: function (response) {
          set_tray_color('tray1', response.tray1);
          set_tray_color('tray2', response.tray2);
          set_tray_color('tray3', response.tray3);
          set_tray_color('tray4', response.tray4);
        },
        error: function (response) {
          console.log(response);
        },
      });
      console.log()
    },
    error: function (response) {
      console.log(response);
    },
  });
}

$(document).ready(function () {
  // Get tasks at page load
  get_and_generate_tasks();
  activate_trays();
  set_next_harvest();

  // Growth Period Input, creates entries in database
  $("#growth_period_button").click(function () {
    growth_period = window.prompt(
      "Enter the estimated growth period (in weeks) for the plant, minimum 4:",
      4
    );

    if (growth_period == null || growth_period == "") return;

    $.ajax({
      type: "GET",
      url: "scheduler",
      data: { growth_period: growth_period },
      success: function (response) {
        get_and_generate_tasks();
        activate_trays();
        set_next_harvest();
      },
      error: function (response) {
        console.log(response);
      },
    });
  });

  //restart cycle, following previous growth period input
  $("#restart_button").click(function () {
    if (confirm("Reset all trays/tasks?")) {
      $.ajax({
        type: "GET",
        url: "scheduler",
        data: { restart: true },
        success: function (response) {
          get_and_generate_tasks();
          activate_trays();
          set_next_harvest();
        },
        error: function (response) {
          console.log(response);
        },
      });
    } else {
      return;
    }
  });

  // Nutrient Calculator
  $("#calculate").click(function () {
    var ec_calc = parseFloat($("#ec_calc").val());
    var water_vol = parseFloat($("#water_vol").val());
    // $("#nutr_vol").text("Loading...");

    // $.ajax({
    //   type: "GET",
    //   url: "latest_sensor_val",
    //   data: { calc: true, target_conc: target_conc, water_vol: water_vol },
    //   success: function (response) {
    //     output = parseFloat(response.nutr_vol).toFixed(1);
    //     $("#nutr_vol").text(output + " ml");
    //   },
    //   error: function (response) {
    //     console.log(response);
    //   },
    // });

    var output = (
      0.02 * water_vol * 1000 -
      (ec_calc / 2) * 0.02 * water_vol * 1000
    ).toFixed(0);
    output > 0
      ? $("#nutr_vol").text(output + " ml")
      : $("#nutr_vol").text("0 ml");
  });

  // Realtime EC/Temp Display + Tray States
  var continuous_call = function () {
    $.ajax({
      type: "GET",
      url: "latest_sensor_val",
      success: function (response) {
        var now = new Date();
        var last_updated = new Date(response.datetime_created);
        var expired = Math.abs(now - last_updated) > 300000; //5 min since last updated

        if (expired) {
          $("#temp_display").text("??");
          $("#ec_display").text("??");
          $("#no_wifi").show();
        } else {
          $("#temp_display").text(response.temp);
          $("#ec_display").text(response.ec);
          $("#no_wifi").hide();
        }

        if (!expired) {
          if (parseFloat(response.ec) < 1.5) {
            $("#ec_ok").text("LOW");
            $("#ec_ok").css("color", color_to_hex("red"));
          } else if (parseFloat(response.ec) > 2.5) {
            $("#ec_ok").text("HIGH");
            $("#ec_ok").css("color", color_to_hex("red"));
          } else {
            $("#ec_ok").text("OK");
            $("#ec_ok").css("color", "#51c528");
          }

          if (parseFloat(response.temp) < 20) {
            $("#temp_ok").text("LOW");
            $("#temp_ok").css("color", color_to_hex("red"));
          } else if (parseFloat(response.temp) > 35) {
            $("#temp_ok").text("HIGH");
            $("#temp_ok").css("color", color_to_hex("red"));
          } else {
            $("#temp_ok").text("OK");
            $("#temp_ok").css("color", "#51c528");
          }
        }
      },
      error: function (response) {
        console.log(response);
      },
    });
  };

  var interval = 3000; // 3 secs
  setInterval(continuous_call, interval);

  var hourly_interval = 3600000; // 1 hour
  setInterval(get_and_generate_tasks(), hourly_interval);
  setInterval(activate_trays(), hourly_interval);
});

/*
==============FUNCTIONS==============
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

function set_tray_stage(tray_class, stage) {
  $("#" + tray_class + "_plant").attr(
    "src",
    "../static/images/" + stage + ".png"
  );
}

//gets tray state from database and sets trays in html. Also changes growth period input text
function activate_trays() {
  $.ajax({
    type: "GET",
    url: "tray_state",
    success: function (response) {
      set_tray_color("tray1", response.tray1);

      set_tray_color("tray2", response.tray2);

      set_tray_color("tray3", response.tray3);

      set_tray_color("tray4", response.tray4);

      //growth state images
      $.ajax({
        type: "GET",
        url: "scheduler",
        success: function (response) {
          last_growth_period =
            4 *
            (parseInt(response.data[1].week) - parseInt(response.data[0].week));
          $("#growth_weeks").text(last_growth_period + " weeks");
          //set_tray_state code further implementation
        },
        error: function (response) {
          console.log(response);
        },
      });
    },
    error: function (response) {
      console.log(response);
    },
  });
}

// Adds singular task card
function add_task(task, tray, color, due_date, first = false) {
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
    " (" +
    tray +
    ")" +
    '</h6> </div> <div class="card-body"> <div class="row"> <div class="col"> <div class="text-uppercase text-info font-weight-bold text-xs mb-1"></div> </div> </div> <div class="row">';

  //trays in card
  for (i = 1; i <= 4; i++) {
    html +=
      '<div class="col-sm-3"> <div class="card"> <div class="card-body" style="background-color: ';
    i == tray ? (html += color) : (html += "#E8E9EC");
    html += ';padding: 10px;height: 54px;"></div> </div> </div> ';
  }

  //task icons (arrow/check)
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

  //footer; clear button
  html +=
    '<div class="card-footer"> <div class="row text-right"> <div class="col" style="height: 26.8571px">';
  var now = new Date();
  var task_date = new Date(due_date).setHours(0, 0, 0, 0);
  // task_date = task_date - (6.048e+8)*2;
  var time_diff = Math.abs(task_date - now);
  var hours_diff = Math.ceil(time_diff / (1000 * 60 * 60));
  var days_diff = Math.ceil(time_diff / (1000 * 60 * 60 * 24));


  // if (first) {
    if (first && now > task_date) {
    html +=
      '<i class="material-icons" style="color: #858796;vertical-align: text-bottom">delete</i><span id="clear_task_button" style="font-family: Lato, sans-serif;font-size: 18px;"> Clear </span>';
  } else if (days_diff == 1) {
    plural = hours_diff > 1 ? "s" : "";
    html +=
      '<span style="font-family: Lato, sans-serif;font-size: 18px;"><em> In ' +
      hours_diff +
      " hour" +
      plural +
      " </em></span>";
  } else {
    plural = days_diff > 1 ? "s" : "";
    html +=
      '<span style="font-family: Lato, sans-serif;font-size: 18px;"><em> In ' +
      days_diff +
      " day" +
      plural +
      " </em></span>";
  }

  html += "</div> </div> </div> </div>";

  $("#task_col").append(html);
}

// delete old cards, get tasks from database, calls add_task to generate html for cards
function get_and_generate_tasks() {
  $.ajax({
    type: "GET",
    url: "scheduler",
    success: function (response) {
      $("#task_col").empty();
      for (let i = 0; i < response.data.length; i++) {
        e = response.data[i];
        let flag = i == 0 ? true : false;

        if (e.to_harvest != "blank") {
          if (e.to_harvest == "red" || e.to_harvest == "orange") {
            add_task("Harvest", 1, e.to_harvest, e.date, flag);
            flag = false;
          } else if (e.to_harvest == "blue" || e.to_harvest == "green") {
            add_task("Harvest", 4, e.to_harvest, e.date, flag);
            flag = false;
          }
        }
        if (e.to_transfer != "blank") {
          if (e.to_transfer == "red" || e.to_transfer == "orange") {
            add_task("Transfer", 2, e.to_transfer, e.date, flag);
            flag = false;
          } else if (e.to_transfer == "blue" || e.to_transfer == "green") {
            add_task("Transfer", 3, e.to_transfer, e.date, flag);
            flag = false;
          }
        }
        if (e.to_plant != "blank") {
          if (e.to_plant == "red" || e.to_plant == "orange") {
            add_task("Plant", 2, e.to_plant, e.date, flag);
            flag = false;
          }
          if (e.to_plant == "blue" || e.to_plant == "green") {
            add_task("Plant", 3, e.to_plant, e.date, flag);
            flag = false;
          }
        }
      }

      //enable task 'clear' button
      setTimeout(function () {
        $("#clear_task_button").click(function () {
          $("#clear_task_button").css("color", "#85879650");
          $("#clear_task_button").off("click");
          if (response.data[0].to_harvest != "blank") {
            complete_task("harvest", response.data[0].to_harvest);
            // console.log("harvest clear");
          } else if (response.data[0].to_transfer != "blank") {
            complete_task("transfer", response.data[0].to_transfer);
          } else if (response.data[0].to_plant != "blank") {
            complete_task("plant", response.data[0].to_plant);
          }
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
      get_and_generate_tasks();
      //modify tray in database
      activate_trays();
      set_next_harvest();
    },
    error: function (response) {
      console.log(response);
    },
  });
}

//get next harvest date
function set_next_harvest() {
  $.ajax({
    type: "GET",
    url: "scheduler",
    data: { next_harvest: true },
    success: function (response) {
      $("#next_harvest").text(response.date);
    },
    error: function (response) {
      console.log(response);
    },
  });
}

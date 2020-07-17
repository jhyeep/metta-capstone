$(document).ready(function () {
  // Growth Period Input
  $("#growth_period_input").click(function () {
    $.ajax({
      type: "GET",
      url: "scheduler",
      data: {'growth_weeks': 8},
      success: function (response) {
        // console.log(response);
        // output = parseFloat(response.nutr_vol).toFixed(1);
        // $("#nutr_vol").text(output + ' ml');
        alert(response)
      },
      error: function (response) {
        console.log(response);
      },
    });
  });

  // Nutrient Calculator
  $("#calculate").click(function () {
    var target_conc = parseFloat($("#target_conc").val());
    var water_vol = parseFloat($("#water_vol").val());

    $.ajax({
      type: "GET",
      url: "latest_sensor_val",
      data: {'calc': true, 'target_conc': target_conc, 'water_vol': water_vol},
      success: function (response) {
        // console.log(response);
        output = parseFloat(response.nutr_vol).toFixed(1);
        $("#nutr_vol").text(output + ' ml');
      },
      error: function (response) {
        console.log(response);
      },
    });
  });

  // Realtime EC/Temp Display
  var ajax_call = function () {

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
  };

  var interval = 3000; // 3 secs
  setInterval(ajax_call, interval);
});

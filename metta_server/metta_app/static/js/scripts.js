$(document).ready(function () {
  // Growth Period Input
  $("#growth_period_input").click(function () {
    alert("hello");
  });

  // Nutrient Calculator
  $("#calculate").click(function () {
    var target_conc = parseFloat($("#calc_conc_input").val());
    var water_vol = parseFloat($("#calc_water_input").val());

    $.ajax({
      type: "GET",
      url: "latest_sensor_val",
      success: function (response) {
        var temp = response.temp;
        // console.log(response);
        var output = target_conc + water_vol + parseFloat(temp); //change this
        $("#nutrient_vol").text(output);
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

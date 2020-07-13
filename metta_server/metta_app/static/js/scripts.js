$(document).ready(function () {
  $("#growth_period_input").click(function () {
    alert("hello");
  });

  $("#calculate").click(function () {

    $.ajax({
      type: "GET",
      url: "latest_temp",
      success: function (response) {
        var temp = response.temp
      },
      error: function (response) {
        console.log(response);
      },
    });

    var target_conc = parseFloat($("#calc_conc_input").val());
    var water_vol = parseFloat($("#calc_water_input").val());

    var output = target_conc + water_vol + temp; //change this
    $("#nutrient_vol").text(output);

  });


});

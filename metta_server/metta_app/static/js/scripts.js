$(document).ready(function () {
  $("#growth_period_input").click(function () {
    alert("hello");
  });

  $("#calculate").click(function () {
    var target_conc = parseFloat($("#calc_conc_input").val())
    var water_vol = parseFloat($("#calc_water_input").val())
    var output = target_conc + water_vol;
    // alert(target_conc + water_vol);
    $("#nutrient_vol").text(output);
  });
});

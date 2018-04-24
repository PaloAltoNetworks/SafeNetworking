// JavaScript Document

/* Nav area calculation */
function calculateNavArea() {
  var windowwidth = $( window ).width();
  var windowheight = $( window ).height();
  var mainnavwidth = $("#main-nav").width();
  var mainnavheight = $("#main-nav").height();
  var ubernavwidth = $("#uber-nav").width() || 0;;
  var ubernavheight = $("#uber-nav").height() || 0;
  var pageheaderwidth = $(".page-header").width() || 0;;
  var pageheaderheight = $(".page-header").height() || 0;

  /* For Traps, count the page header in the nav calculation when layout is fixed */
  if ( $( "#uber-nav" ).hasClass( "nav-fixed" )  && $( "body" ).hasClass( "traps" ) ) {
    var percentage = ((mainnavwidth * mainnavheight) + (ubernavwidth * ubernavheight)  + (pageheaderwidth * pageheaderheight))/(windowwidth * windowheight) * 100;
  }
  else {
    var percentage = ((mainnavwidth * mainnavheight) + (ubernavwidth * ubernavheight))/(windowwidth * windowheight) * 100;
  }
  $("#navpercent").text(percentage.toFixed(1));



}

$(window).load(function() {
  calculateNavArea();
});


$(window).resize(function() {
  calculateNavArea();
});

$("#nav-top").click(function(){
  $("#nav-container").addClass("top-nav");
  $("#nav-container").removeClass("left-nav");
  $("#uber-nav").removeClass("uber-left");
  calculateNavArea();
});

$("#nav-left").click(function(){
  $("#nav-container").removeClass("top-nav");
  $("#nav-container").addClass("left-nav");
  $("#uber-nav").addClass("uber-left");
  calculateNavArea();
});

$("#nav-left-sm").click(function(){
  $("#nav-container").removeClass("top-nav");
  $("#nav-container").addClass("left-nav").addClass("left-nav-sm");
  $("#uber-nav").addClass("uber-left");
  calculateNavArea();
});

$("#top-white").click(function(){
    $("#uber-nav").removeClass("navbar-inverse").addClass("navbar-light");
});

$("#top-black").click(function(){
    $("#uber-nav").addClass("navbar-inverse").removeClass("navbar-light");

});

$("#nav-color-black").click(function(){
    $("#uber-nav").addClass("navbar-inverse").removeClass("navbar-light").removeClass("navbar-blue");
    $("body").removeClass("blue").removeClass("app-specific");
});

$("#nav-color-blue").click(function(){
    $("#uber-nav").addClass("navbar-inverse").removeClass("navbar-light").addClass("navbar-blue");
    $("body").addClass("blue").removeClass("app-specific");
     //$this.attr("href", _href + '?nav-blue');
});

$("#nav-color-app-specific").click(function(){
    $("#uber-nav").addClass("navbar-inverse").removeClass("navbar-light");
    $("body").addClass("app-specific").removeClass("blue");
    $("a.app-link").each(function() {
     var $this = $(this);
     var _href = $this.attr("href");
     //$this.attr("href", _href + '?color-me');
    });
});


$("#nav-fixed").click(function(){
    $("body").addClass("nav-fixed");
    calculateNavArea();
});

$("#nav-fluid").click(function(){
    $("body").removeClass("nav-fixed");
    calculateNavArea();
});



/* Search Box Animation */

$("#search").click(function(){
  $("#search-box").toggleClass("search-box-open");
  $(this).toggleClass("search-icon-on");
});

/* Control Panel, style switching */

$(".control-panel").find("a").click(function(){
  $(this).parent().find("a").removeClass("control-on");
  $(this).addClass("control-on"); return false
});

$("#logo1").click(function(){
  $(".pan-logo-area").show();
  $(".pan-logo-area2").hide();
});

$("#logo2").click(function(){
  $(".pan-logo-area").hide();
  $(".pan-logo-area2").show();
});

$("#filters-left").click(function(){
  $("#page").removeClass("filters-right");
});

$("#filters-right").click(function(){
  $("#page").addClass("filters-right");
});



$("#tab1").click(function(){
  $("#navbar-top").removeClass("navbar2");
  $("#navbar-top").removeClass("navbar3");
});

$("#tab2").click(function(){
  $("#navbar-top").addClass("navbar2");
  $("#navbar-top").removeClass("navbar3");
});

$("#tab3").click(function(){
  $("#navbar-top").removeClass("navbar2");
  $("#navbar-top").addClass("navbar3");
});


$("#density1").click(function(){
  $("body").removeClass("more-dense");
  $("body").addClass("less-dense");
});

$("#density2").click(function(){
  $("body").removeClass("more-dense");
  $("body").removeClass("less-dense");
});

$("#density3").click(function(){
  $("body").addClass("more-dense");
  $("body").removeClass("less-dense");
});

$("#close-control-panel").click(function(){
  $(".control-panel").hide(); return false
});


/* Filters */

$(".filter-name").click(function(){
  $(this).next().toggle();
  $(this).parent().toggleClass("filter-group-closed");
});


// Tooltips
$('[data-toggle="tooltip"]').tooltip()

/* Magna */

$("#magna-toggle-diagram").click(function(){
  $("#view-timeline").hide();
  $("#view-diagram").show();
  $("#magna-toggle-diagram").addClass("btn-primary").removeClass("btn-secondary");
  $("#magna-toggle-timeline").removeClass("btn-primary").addClass("btn-secondary");
});

$("#magna-toggle-timeline").click(function(){
  $("#view-timeline").show();
  $("#view-diagram").hide();
  $("#magna-toggle-timeline").addClass("btn-primary").removeClass("btn-secondary");
  $("#magna-toggle-diagram").removeClass("btn-primary").addClass("btn-secondary");
});

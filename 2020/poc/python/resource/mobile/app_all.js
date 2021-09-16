$( "#theme-selector input" ).on( "change", function( event ) {
    var themeClass = $( "#theme-selector input:checked" ).attr( "id" );

    $( "#id_application_container_view_module" ).removeClass( "ui-page-theme-a ui-page-theme-b" ).addClass( "ui-page-theme-" + themeClass );
    $( "#ui-body-test" ).removeClass( "ui-body-a ui-body-b" ).addClass( "ui-body-" + themeClass );
    $( "#ui-bar-test, #ui-bar-form" ).removeClass( "ui-bar-a ui-bar-b" ).addClass( "ui-bar-" + themeClass );
    $( ".ui-collapsible-content" ).removeClass( "ui-body-a ui-body-b" ).addClass( "ui-body-" + themeClass );
    $( ".theme" ).text( themeClass );
});
$( "#opt-shadow input" ).on( "change", function( event ) {
    if ( $( "#on" ).prop( "checked" ) ) {
        $( "#id_application_container_view_module" ).removeClass( "noshadow" );
    } else if ( $( "#off" ).prop( "checked" ) ) {
        $( "#id_application_container_view_module" ).addClass( "noshadow" );
    }
});
$( "#opt-navbars input" ).on( "change", function( event ) {
    if ( $( "#show" ).prop( "checked" ) ) {
        $( "#id_application_container_view_module .ui-navbar" ).show();
        $( "#id_application_container_view_module .ui-footer h4" ).hide();
    } else if ( $( "#hide" ).prop( "checked" ) ) {
        $( "#id_application_container_view_module .ui-navbar" ).hide();
        $( "#id_application_container_view_module .ui-footer h4" ).show();
    }
});

console.log("app.js loaded");
/**
 * Created by Admin on 17-01-2016.
 */

$(document).ready(function(){


   $( "#tags" ).autocomplete({
                        source: restaurantAutocompleteUrl,
                        selectFirst: true,
                        minLength: 2
   });

});
        /**
 * Created by Admin on 22-02-2016.
 */
      $(document).ready(function(){
         $(".rating").click(function() {
        var selectedVal = "";
var selected = $("input[type='radio'][class='star']:checked");
if (selected.length > 0) {
    selectedVal = selected.val();
}
          alert(selectedVal);
});

      });
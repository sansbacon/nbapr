<script type="text/javascript" charset="utf8" src="//code.jquery.com/jquery-1.10.2.min.js"></script>
<script type="text/javascript" charset="utf8" src="//cdn.datatables.net/1.10.7/js/jquery.dataTables.js"></script>
<link rel="stylesheet" type="text/css" href="//cdn.datatables.net/1.10.7/css/jquery.dataTables.css">

<script type="text/javascript">
var url = "https://raw.githubusercontent.com/sansbacon/nbapr/main/data/player-rater-9cat.json";
$(document).ready(function() {
  var oTable = $('#pr').DataTable( {
    "ajax": url,
    "iDisplayLength": 250,
    "dom": '<"pull-left"f><"pull-right"l>t',
    "order": [3, 'desc'],
    "columnDefs": [
        {"className": "dt-center", "targets": "_all"}
      ]
    } );

  oTable.$('th').tooltip( {
      "delay": 0,
      "track": true,
      "fade": 250
  } );

  $.fn.dataTable.ext.errMode = 'none';
  $('#pr')
    .on( 'error.dt', function ( e, settings, techNote, message ) {
    console.log( 'An error has been reported by DataTables: ', message );
    alert('Request failed: please use valid values');
  }).DataTable();
});
</script>

# NBA Player Rater: 9 Category

{% include 'table.md' %}

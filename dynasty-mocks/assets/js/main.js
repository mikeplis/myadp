$(document).ready(function() {

  var tableId = 'data'

  if ($('#' + tableId).length > 0) {

    $('#' + tableId + ' thead th').eq(1).each( function () {
      var title = $('#' + tableId + ' thead th').eq( $(this).index() ).text();
      $(this).html( '<input type="text" placeholder="Search '+title+'" />' );
    } );

    var t = $('#' + tableId).DataTable({
      "ajax": {
        "url": "generate_report",
        "data": apiData // defined in table.html
      },
      "paging": false,
      "processing": true,
      "dom": 'T<"clear">lrtip',
      "columnDefs": [
        {
          "render": function(data, type, row, meta) {
            return data.toFixed(1);
          },
          "targets": [4, 5]
        },
        {
          "orderable": false,
          "targets": [1,2,3]
        }
      ],
      "tableTools": {
          "sSwfPath": "/static/swf/copy_csv_xls_pdf.swf",
          "sRowSelect": "os",
          // if sSelectedClass is changed, must also change selected class in _fnFilterColumn in datatables js file
          "sSelectedClass": "selected",
          "aButtons": []
      },
      initComplete: function (settings) {
        // show processing indicator only when data is loading; if we just hide() it'll flash every time we sort, search, etc
        $(".dataTables_processing").remove()

        var api = this.api();
        api.order([4, 'asc']).draw();
        $([2, 3]).each(function(_, i) {
          var column = api.column(i);
          var select = $('<select><option value=""></option></select>')
            .appendTo( $(column.header()).empty() )
            .on('change', function() {
              var val = $.fn.dataTable.util.escapeRegex(
                $(this).val() 
              );
              column
                .search( val ? '^'+val+'$' : '', true, false )
                .draw();
            });
          column.data().unique().sort().each( function ( d, j ) {
              select.append( '<option value="'+d+'">'+d+'</option>' )
          });
        });
      }
    });

    t.columns().eq(0).each( function ( colIdx ) {
        $( 'input', t.column( colIdx ).header() ).on( 'keyup change', function () {
            t
                .column( colIdx )
                .search( this.value )
                .draw();
        } );
    } );

    t.on('order.dt search.dt', function() {
      t.column(0, {search:'applied', order:'applied'}).nodes().each(function(cell, i) {
        cell.innerHTML = i+1;
      });
    }).draw();
  }
});
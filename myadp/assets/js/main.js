$(document).ready(function() {

  var tableId = '#data'

  // necessary here until I figure out how to only load main.js on a page with a table (e.g. not the home page)
  if ($(tableId).length > 0) {

    var over = '<div id="overlay">' +
            '<img id="loading" src="/static/images/ajax-loader.gif">' +
            '</div>';
    $(over).appendTo(tableId);

    $(tableId + ' thead th').eq(1).each( function () {
      var title = $(tableId + ' thead th').eq( $(this).index() ).text();
      $(this).html( '<input type="text" placeholder="Search '+title+'" />' );
    } );

    var t = $(tableId).DataTable({
      "ajax": {
        "url": "/generate",
        "data": apiData // defined in table.html
      },
      "paging": false,
      "scrollCollapse": true,
      "scrollY": "75%",
      "scrollX": true,
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
          // "sSwfPath": "/static/swf/copy_csv_xls_pdf.swf",
          "sSwfPath": "http://cdn.datatables.net/tabletools/2.2.2/swf/copy_csv_xls_pdf.swf",
          "sRowSelect": "os",
          // if sSelectedClass is changed, must also change selected class in _fnFilterColumn in datatables js file
          "sSelectedClass": "selected",
          "aButtons": [
            {
              "sExtends": "csv",
              "sButtonText": "Export to CSV",
              // export all columns except for the first column (Rank)
              "mColumns": function (x) { 
                var columnIndexes = [];
                for (i = 1; i < x['aoColumns'].length; i++) { columnIndexes.push(i); }
                return columnIndexes;
              }
            }
          ]
      },
      initComplete: function (settings) {
        $('#overlay').hide();

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
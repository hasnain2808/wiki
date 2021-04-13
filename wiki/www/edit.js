frappe.ready(async () => {
  debugger;
  new EditAsset();
});

// function render_preview() {
//     // frappe.ready(() => {
// 		$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
//             debugger
// 			let activeTab = $(e.target);

// 			if (activeTab.prop('id') === 'preview-tab') {
//                 console.log("in")
// 				let content = $('textarea#content').val();
// 				let $preview = $('.wiki-preview');
// 				$preview.html('Loading preview...');
// 				frappe.call({
//                     method: 'wiki.www.edit.preview',
//                     args : {
//                         content : content,
//                         path : window.location.search
//                     },
//                     callback: r => {
//                         if (r.message) {
//                             $preview.html(r.message);
//                         }
//                     }
//                 })
// 			}

// 			if (activeTab.prop('id') === 'diff-tab') {
//                 console.log("diff")
// 			}

// 		})
// 	// })
// }

class EditAsset {
  constructor(opts) {
    // Object.assign(this, opts);
    // this.dialog_manager = new erpnext.accounts.bank_reconciliation.DialogManager(
    // 	this.company,
    // 	this.bank_account
    // );
    // this.make_dt();

    console.log("in js");
    this.make_code_field_group();
    this.make_edit_field_group();
    this.render_preview();
  }

  render_preview() {
    // frappe.ready(() => {
    $('a[data-toggle="tab"]').on("shown.bs.tab",  (e) => {
      debugger;
      let activeTab = $(e.target);

      if (activeTab.prop("id") === "preview-tab") {
        console.log("in");
        let content = $("textarea#content").val();
        let $preview = $(".wiki-preview");
        $preview.html("Loading preview...");
        frappe.call({
          method: "wiki.www.edit.preview",
          args: {
            content: this.code_field_group.get_value('code'),
            path: window.location.search,
          },
          callback: (r) => {
            if (r.message) {
              $preview.html(r.message);
            }
          },
        });
      }

      if (activeTab.prop("id") === "diff-tab") {
        console.log("diff");
      }
    });
    // })
  }

  make_edit_field_group() {
    const route = $("#route").val();
    this.edit_field_group = new frappe.ui.FieldGroup({
      fields: [
        {
          label: __("Route Link"),
          fieldname: "route_link",
          fieldtype: "Data",
          default: route || "",
        },
        {
          label: __("Edit Code"),
          fieldname: "code",
          fieldtype: "Button",
          click: () => this.update_code(),
        },
      ],
      body: $(".routedisp"),
    });
    this.edit_field_group.make();
  }

  make_code_field_group() {
    this.code_field_group = new frappe.ui.FieldGroup({
      fields: [
        {
          label: __("Edit Code"),
          fieldname: "code",
          fieldtype: "Code",
          columns: 4,
          reqd: 1,
          options: "Markdown",
        },
      ],
      body: $(".wiki-write").get(0),
    });
    this.code_field_group.make();
  }

  update_code() {
    frappe.call( {
        method: "wiki.www.edit.get_code",
        args: {route:  this.edit_field_group.get_value("route_link")},
        callback: (r) => {
            console.log(r)
            this.code_field_group.get_field('code').set_value(r.message)
        }
    })

  }
}

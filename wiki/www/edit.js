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
    this.make_code_field_group();
    this.make_edit_field_group();
    this.make_submit_section_field_group();
    this.render_preview();
    this.add_attachment_handler();
  }

  render_preview() {
    // frappe.ready(() => {
    $('a[data-toggle="tab"]').on("shown.bs.tab", (e) => {
      debugger;
      let activeTab = $(e.target);

      if (activeTab.prop("id") === "preview-tab") {
        console.log("in");
        let content = $("textarea#content").val();
        let $preview = $(".wiki-preview");
        let $diff = $(".wiki-diff");
        $preview.html("Loading preview...");
        frappe.call({
          method: "wiki.www.edit.preview",
          args: {
            content: this.code_field_group.get_value("code"),
            path: window.location.search,
          },
          callback: (r) => {
            if (r.message) {
              $preview.html(r.message.html);
              $diff.html(r.message.diff);
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
    frappe.call({
      method: "wiki.www.edit.get_code",
      args: { route: this.edit_field_group.get_value("route_link") },
      callback: (r) => {
        console.log(r);
        this.code_field_group.get_field("code").set_value(r.message);
      },
    });
  }
  make_submit_section_field_group() {
    this.submit_section_field_group = new frappe.ui.FieldGroup({
      fields: [
        {
          label: __("Edit Message Short/ Pull Request Title"),
          fieldname: "edit_message_short",
          fieldtype: "Data",
          reqd: 1,
        },
        {
          label: __("Edit Message Long/ Pull Request Body"),
          fieldname: "edit_message_long",
          fieldtype: "Text",
        },
        {
          label: __("Submit"),
          fieldname: "submit_button",
          fieldtype: "Button",
          primary: 1,
          btn_size: "lg",
          reqd: 1,
          click: () => this.raise_pr(),
        },
      ],
      body: $(".submit-section"),
    });
    this.submit_section_field_group.make();
  }

  raise_pr() {
    frappe.call({
      method: "wiki.www.edit.update",
      args: {
        content: this.code_field_group.get_value("code"),
        route: this.edit_field_group.get_value("route_link"),
        edit_message_short: this.submit_section_field_group.get_value(
          "edit_message_short"
        ),
        edit_message_long: this.submit_section_field_group.get_value(
          "edit_message_long"
        ),
      },
      callback: (r) => {
        if (r.message) {
          $preview.html(r.message.html);
          $diff.html(r.message.diff);
        }
      },
    });
  }

  add_attachment_handler() {
    var me = this;
    $(".add-attachment").click(function () {
      me.new_attachment();
    });
  }

  new_attachment(fieldname) {
    if (this.dialog) {
      // remove upload dialog
      this.dialog.$wrapper.remove();
    }

    new frappe.ui.FileUploader({
      folder: "Home/Attachments",
      on_success: (file_doc) => {
        if (!this.attachments) this.attachments=[]
        if (!this.save_paths) this.save_paths={}
        this.attachments.push(file_doc)
        console.log(this.attachments)
        this.build_attachment_table()
      },
    });
  }

  build_attachment_table(){
    var wrapper = $('.wiki-attachment')
    wrapper.empty()

    var table = $('<table class="table table-bordered" style="cursor:pointer; margin:0px;"><thead>\
    <tr><th style="width: 33%">'+__('File Name')+'</th><th style="width: 33%">'+__('Current Path')+ '</th><th>'+__('Path While Submitting') +'</th></tr>\
    </thead><tbody></tbody></table>').appendTo(wrapper);
  $('<p class="text-muted small">' + __("Click table to edit") + '</p>').appendTo(wrapper);


    this.attachments.forEach(f => {
    const row = $("<tr></tr>").appendTo(table.find("tbody"));
    $("<td>" + f.file_name + "</td>").appendTo(row);
    $("<td>" + f.file_url + "</td>").appendTo(row);
    $("<td>" + f.save_path +"</td>")
      .appendTo(row);
  });
  var  me = this;
  var dfs=[]
  this.attachments.forEach(f =>{
    dfs.push({
      fieldname: f.file_name,
      fieldtype: "Data",
      label: f.file_name
    })
  })
  table.on('click', function() {
    var dialog = new frappe.ui.Dialog({
      fields: dfs,
      primary_action: function() {
        var values = this.get_values();
        if(values) {
          this.hide();
          // frm.set_value('filters', JSON.stringify(values));
          me.save_paths = values
          me.attachments.forEach(f => {
            f.save_path = values[f.file_name]
          })
          console.log(values)
          console.log(me.attachments)
          me.build_attachment_table()
        }
      }
    });
    dialog.show();
    dialog.set_values(me.save_paths);
  })
  }
}

function remove_loader(name) {
  $(name).removeClass("active").addClass("disabled");
}
function add_loader(name) {
  $(name).addClass("active").removeClass("disabled");
}

$(document).ready(function () {
  $("#main-menu-toggle").on("click", function () {
    $("#main-menu-sidebar")
      .sidebar({
        dimPage: false,
        transition: "overlay",
      })
      .sidebar("toggle");
  });
  $("#admin-sidebar-toggle").on("click", function () {
    $("#admin-sidebar")
      .sidebar({
        dimPage: false,
        transition: "overlay",
      })
      .sidebar("toggle");
  });
  $("#secondary-menu")
    .children(".ui .item")
    .on("click", function () {
      $("#secondary-menu").children(".ui .item").removeClass("active");
      $(this).addClass("active");

      var id = $(this).attr("tab-id");
      var path = window.location.pathname.replace(/\/$/, "");
      path = path.substr(0, path.lastIndexOf("/") + 1) + id + "/";
      window.history.pushState(null, null, path);

      id = "#" + id;
      $(".tab-content").children(".tab").removeClass("active");
      $(id).addClass("active");

      function update_url() {
        return window.location.href.replace(/(\d+)(\.html)$/, function (
          str,
          p1,
          p2
        ) {
          return Number(p1) + 1 + p2;
        });
      }
    });
  // allow system messages to be closed
  $(".message .close").on("click", function () {
    $(this).closest(".message").transition("fade");
  });

  $(".ui.dropdown").dropdown();

  // toggle language
  $(".lang").on("click", function () {
    var lang = $(this).attr("lang-code");
    $("#language").val(lang);
    $("#language-form").submit();
  });
});

$(".admin-sidebar-header").on("click", function (e) {
  e.preventDefault();
  if ($(this).parent(".item").hasClass("collapsed")) {
    $(this).parent(".item").removeClass("collapsed");
  } else {
    $(this).parent(".item").addClass("collapsed");
  }
});

function copy(that) {
  var value = document.getElementById("value-to-copy");
  value.select();
  document.execCommand("copy", false);
}

$(".copy.button").popup({
  on: "click",
});

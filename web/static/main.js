"use strict";
var _typeof =
  "function" == typeof Symbol && "symbol" == typeof Symbol.iterator
    ? function (e) {
        return typeof e;
      }
    : function (e) {
        return e &&
          "function" == typeof Symbol &&
          e.constructor === Symbol &&
          e !== Symbol.prototype
          ? "symbol"
          : typeof e;
      };
!(function (e) {
  var t = !1;
  if (
    ("function" == typeof define && define.amd && (define(e), (t = !0)),
    "object" ===
      ("undefined" == typeof exports ? "undefined" : _typeof(exports)) &&
      ((module.exports = e()), (t = !0)),
    !t)
  ) {
    var n = window.Cookies,
      o = (window.Cookies = e());
    o.noConflict = function () {
      return (window.Cookies = n), o;
    };
  }
})(function () {
  function p() {
    for (var e = 0, t = {}; e < arguments.length; e++) {
      var n = arguments[e];
      for (var o in n) t[o] = n[o];
    }
    return t;
  }
  return (function e(f) {
    function k(e, t, n) {
      var o;
      if ("undefined" != typeof document) {
        if (1 < arguments.length) {
          if (
            "number" == typeof (n = p({ path: "/" }, k.defaults, n)).expires
          ) {
            var c = new Date();
            c.setMilliseconds(c.getMilliseconds() + 864e5 * n.expires),
              (n.expires = c);
          }
          n.expires = n.expires ? n.expires.toUTCString() : "";
          try {
            (o = JSON.stringify(t)), /^[\{\[]/.test(o) && (t = o);
          } catch (e) {}
          (t = f.write
            ? f.write(t, e)
            : encodeURIComponent(String(t)).replace(
                /%(23|24|26|2B|3A|3C|3E|3D|2F|3F|40|5B|5D|5E|60|7B|7D|7C)/g,
                decodeURIComponent
              )),
            (e = (e = (e = encodeURIComponent(String(e))).replace(
              /%(23|24|26|2B|5E|60|7C)/g,
              decodeURIComponent
            )).replace(/[\(\)]/g, escape));
          var i = "";
          for (var r in n)
            n[r] && ((i += "; " + r), !0 !== n[r] && (i += "=" + n[r]));
          return (document.cookie = e + "=" + t + i);
        }
        e || (o = {});
        for (
          var a = document.cookie ? document.cookie.split("; ") : [],
            l = /(%[0-9A-Z]{2})+/g,
            s = 0;
          s < a.length;
          s++
        ) {
          var d = a[s].split("="),
            u = d.slice(1).join("=");
          this.json || '"' !== u.charAt(0) || (u = u.slice(1, -1));
          try {
            var m = d[0].replace(l, decodeURIComponent);
            if (
              ((u = f.read
                ? f.read(u, m)
                : f(u, m) || u.replace(l, decodeURIComponent)),
              this.json)
            )
              try {
                u = JSON.parse(u);
              } catch (e) {}
            if (e === m) {
              o = u;
              break;
            }
            e || (o[m] = u);
          } catch (e) {}
        }
        return o;
      }
    }
    return (
      ((k.set = k).get = function (e) {
        return k.call(k, e);
      }),
      (k.getJSON = function () {
        return k.apply({ json: !0 }, [].slice.call(arguments));
      }),
      (k.defaults = {}),
      (k.remove = function (e, t) {
        k(e, "", p(t, { expires: -1 }));
      }),
      (k.withConverter = e),
      k
    );
  })(function () {});
}),
  (function () {
    var e = document.getElementsByClassName("to-dark")[0],
      t = document.getElementsByClassName("to-white")[0];
    e &&
      t &&
      ((e.onclick = function () {
        document.body.classList.remove("white"),
          document.body.classList.add("dark"),
          Cookies.set("theme", "dark", { expires: 365 });
      }),
      (t.onclick = function () {
        document.body.classList.remove("dark"),
          document.body.classList.add("white"),
          Cookies.set("theme", "white", { expires: 365 });
      }));
  })(),
  (function () {
    var e = document.getElementsByClassName("share")[0],
      t = document.getElementById("share-modal"),
      n = document.querySelector("#share-modal .close");
    function o() {
      t.classList.remove("active");
    }
    e &&
      t &&
      n &&
      ((e.onclick = function () {
        t.classList.add("active");
      }),
      (n.onclick = function () {
        o();
      }),
      (t.onclick = function (e) {
        e.target === t && o();
      }));
  })(),
  (function () {
    var e = document.querySelector("#share-modal .link-input input"),
      t = document.querySelector("#share-modal .link-input .copy"),
      n = void 0;
    e &&
      t &&
      ((e.onclick = function () {
        e.focus(), e.select();
      }),
      (t.onclick = function () {
        e.focus(),
          e.select(),
          document.execCommand("copy"),
          t.classList.add("copied"),
          clearTimeout(n),
          (n = setTimeout(function () {
            t.classList.remove("copied");
          }, 1e3));
      }));
  })(),
  (function () {
    var e = document.querySelectorAll("#share-modal .social-links a"),
      t = Math.round((screen.height - 400) / 2),
      n = Math.round((screen.width - 600) / 2);
    e.forEach(function (e) {
      e.onclick = function () {
        return (
          window.open(
            this.href,
            "share_modal",
            "width=600,height=400,top=" + t + ",left=" + n
          ),
          !1
        );
      };
    });
  })(),
  (function () {
    var e = document.getElementById("contacts"),
      t = document.getElementById("contacts-modal"),
      n = document.querySelector("#contacts-modal .close");
    function o() {
      t.classList.remove("active");
    }
    e &&
      t &&
      n &&
      ((e.onclick = function () {
        t.classList.add("active");
      }),
      (n.onclick = function () {
        o();
      }),
      (t.onclick = function (e) {
        e.target === t && o();
      }));
  })(),
  (function () {
    function t(e, t) {
      yaCounter49397506.reachGoal(e, t);
    }
    var e = document.getElementsByClassName("share")[0],
      n = document.getElementById("contacts"),
      o = document.querySelector(".player-info .top-info .kinopoisk"),
      c = document.querySelector(".player-info .top-info .imdb"),
      i = document.querySelector(".player-info .top-info .world-art"),
      r = document.querySelector(".theme-switcher .to-white"),
      a = document.querySelector(".theme-switcher .to-dark"),
      l = document.querySelector(".user-info .info a"),
      s = document.querySelector(".user-info .image a"),
      d = document.querySelector("#share-modal .link-input .copy"),
      u = document.querySelector("#share-modal .link-input input"),
      m = document.querySelectorAll(".modal-wrapper .close"),
      f = document.querySelectorAll(".modal-wrapper"),
      k = document.querySelector("#share-modal .social-links .vk"),
      p = document.querySelector("#share-modal .social-links .facebook"),
      h = document.querySelector("#share-modal .social-links .twitter"),
      y = document.querySelector("#share-modal .social-links .google-plus"),
      v = document.querySelector("#share-modal .social-links .ok-ru");
    e &&
      e.addEventListener("click", function () {
        t("share_click");
      }),
      n &&
        n.addEventListener("click", function () {
          t("contacts_click");
        }),
      o &&
        o.addEventListener("click", function () {
          t("kinopoisk_click");
        }),
      c &&
        c.addEventListener("click", function () {
          t("imdb_click");
        }),
      i &&
        i.addEventListener("click", function () {
          t("worldart_click");
        }),
      r &&
        a &&
        (r.addEventListener("click", function () {
          t("theme_switch", { target_theme: "white" });
        }),
        a.addEventListener("click", function () {
          t("theme_switch", { target_theme: "dark" });
        })),
      l &&
        l.addEventListener("click", function () {
          t("user_link_click");
        }),
      s &&
        s.addEventListener("click", function () {
          t("user_image_click");
        }),
      d &&
        d.addEventListener("click", function () {
          t("share_link_copy");
        }),
      u &&
        u.addEventListener("click", function () {
          t("share_link");
        }),
      m &&
        m.forEach(function (e) {
          e.addEventListener("click", function () {
            t("modal_close_button");
          });
        }),
      f &&
        f.forEach(function (e) {
          e.addEventListener("click", function (e) {
            e.target === this && t("modal_close_bg");
          });
        }),
      k &&
        k.addEventListener("click", function () {
          t("vk_share");
        }),
      p &&
        p.addEventListener("click", function () {
          t("facebook_share");
        }),
      h &&
        h.addEventListener("click", function () {
          t("twitter_share");
        }),
      y &&
        y.addEventListener("click", function () {
          t("google_plus_share");
        }),
      v &&
        v.addEventListener("click", function () {
          t("ok_share");
        });
  })();

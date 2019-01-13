// Modified from https://github.com/Cople/SocialSharer
import QRCode from 'qrcode'


function getMetaContentByName(name) {
    const el = document.querySelector(`meta[name='${name}']`);
    return el ? el.content : el;
}

function getOpenGraphByName(name) {
    const el = document.querySelector(`meta[property='${name}']`);
    return el ? el.content : el;
}

function getCanonicalURL() {
    const el = document.querySelector("link[rel='canonical']");
    return el ? el.href : el;
}

const extend = Object.assign || function(target, source) {
    if (target === undefined || target === null) {
        return target;
    }

    for (let key in source) {
        if (source.hasOwnProperty(key)) target[key] = source[key];
    }
    return target;
};

const SocialSharer = function() {
    this.init.apply(this, arguments);
};

let defaults = SocialSharer.defaults = {
    url: getOpenGraphByName("og:url") || getCanonicalURL() || location.href,
    title: getOpenGraphByName("og:title") || document.title,
    summary: getOpenGraphByName("og:description") || getMetaContentByName("description") || "",
    pic: getOpenGraphByName("og:image") || (document.images.length ? document.images[0].src : ""),
    source: getOpenGraphByName("og:site_name") || "",
    weiboKey: "",
    twitterVia: "",
    twitterHashTags: "",
    wechatTitle: "分享到微信",
    wechatTip: "用微信「扫一扫」上方二维码即可。",
    qrcodeSize: 160,
    services: ["weibo", "wechat", "qzone", "qq", "douban", "yingxiang"],
    classNamePrefix: "icon icon-",
    onRender: null,
    onClick: null
};

let templates = SocialSharer.templates = {
    weibo: "http://service.weibo.com/share/share.php?url={url}&title={title}&pic={pic}&appkey={weiboKey}",
    qq: "http://connect.qq.com/widget/shareqq/index.html?url={url}&title={title}&summary={summary}&pics={pic}&site={source}",
    qzone: "http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url={url}&title={title}&summary={summary}&pics={pic}&site={source}",
    douban: "https://www.douban.com/share/service?url={url}&title={title}&text={summary}&image={pic}",
    facebook: "https://www.facebook.com/sharer/sharer.php?u={url}",
    twitter: "https://twitter.com/intent/tweet?url={url}&text={title}&via={twitterVia}&hashtags={twitterHashTags}",
    gplus: "https://plus.google.com/share?url={url}",
    linkedin: "http://www.linkedin.com/shareArticle?mini=true&url={url}&title={title}&summary={summary}&source={source}",
    evernote: "http://www.evernote.com/clip.action?url={url}&title={title}",
    yingxiang: "http://app.yinxiang.com/clip.action?url={url}&title={title}",
    email: "mailto:?subject={title}&body={url}",
    webshare: "javascript:;"
};

SocialSharer.addService = function(name, template) {
    templates[name] = template;
    template.replace(/\{(.*?)\}/g, (match, key) => {
        defaults[key] = "";
    });
};

SocialSharer.prototype = {
    constructor: SocialSharer,

    init(container, options) {
        this.container = typeof container === "string" ? document.querySelector(container) : container;

        if (this.container._SocialSharer) return;

        this.container._SocialSharer = this;

        this.options = extend(defaults, this.mergeOptions(options || {}));
        this.options.qrcodeSize *= Math.min(2, window.devicePixelRatio || 1);

        this.createIcons();
    },

    mergeOptions(options) {
        let key, value;

        for (key in defaults) {
            if (key === "onRender" || key === "onClick") continue;

            value = this.container.getAttribute(`data-${key.replace(/[A-Z]/g, "-$&").toLowerCase()}`);

            if (value) {
                options[key] = key === "services" ? value.split(",") : value;
            }
        }

        return options;
    },

    setIcon(icon, service) {
        const self = this;

        icon.className += ` ${this.options.classNamePrefix}${service}`;

        if (service === "wechat") {
            this.createQRCode(icon);
            icon.href = "javascript:;";
        } else {
            icon.href = this.getURL(service);
            if (service !== "email") icon.target = "_blank";
        }

        if (this.options.onClick) {
            icon.onclick = function(event) {
                return self.options.onClick.call(self, event, service);
            };
        }

        if (service === "webshare") {
            icon.origOnClick = icon.onclick;

            icon.onclick = function(event) {
                navigator.share({
                    title: self.options.title,
                    text: self.options.text,
                    url: self.options.url
                });

                if (icon.origOnClick) icon.origOnClick(event);
            };
        }

        if (this.options.onRender) {
            this.options.onRender.call(this, icon, service);
        }
    },

    createIcons() {
        const defaultIcons = this.container.querySelectorAll("[data-service]");
        let i, len, icon, service;

        if (defaultIcons.length) {
            for (i = 0, len = defaultIcons.length; i < len; i++) {
                icon = defaultIcons[i];
                service = icon.getAttribute("data-service");

                if (service === "webshare" && !navigator.share) {
                    this.container.removeChild(icon);
                    continue;
                }

                this.setIcon(icon, service);
            }
        } else {
            for (i = 0, len = this.options.services.length; i < len; i++) {
                service = this.options.services[i];

                if (service === "webshare" && !navigator.share) continue;

                icon = document.createElement("a");

                this.setIcon(icon, service);

                this.container.appendChild(icon);
            }
        }
    },

    createQRCode(icon) {
        const box = document.createElement("div");
        box.className = "qrcode-box";
        QRCode.toDataURL(this.options.url)
        .then(url => {
          box.innerHTML = `<h4>${this.options.wechatTitle}</h4><img src='${url}' /><p>${this.options.wechatTip}</p>`;
        })
        .catch(err => {
          console.error(err)
        });
        icon.appendChild(box);
    },

    getURL(service) {
        const template = templates[service];
        const options = this.options;
        return template ? template.replace(/\{(.*?)\}/g, (match, key) => {
            return encodeURIComponent(options[key]);
        }) : template;
    }
};


export default SocialSharer;

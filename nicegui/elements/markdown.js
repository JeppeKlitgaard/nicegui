export default {
  template: `<div></div>`,
  mounted() {
    this.update(this.content);
  },
  methods: {
    update(content) {
      this.$el.innerHTML = content;
      this.$el.querySelectorAll(".mermaid-pre").forEach((pre, i) => {
        const code = decodeHtml(pre.children[0].innerHTML);
        mermaid.render(`mermaid_${this.$el.id}_${i}`, code, (svg) => (pre.innerHTML = svg));
      });
    },
  },
  props: {
    content: String,
  },
};

function decodeHtml(html) {
  const txt = document.createElement("textarea");
  txt.innerHTML = html;
  return txt.value;
}

import{_ as e,ad as a,ae as t,j as s,P as o,k as i,c as l,l as r,n as d,J as n,x as m,p as u,$ as p,a0 as c,b as f}from"./index.js";import{D as v}from"./index5.js";import{S as h}from"./index4.js";const b={type:"movie",ids:""},g=[{value:"movie",label:"Movie"},{value:"book",label:"Book"},{value:"game",label:"Game"}],y={name:"favorite",components:{Sticky:h,Dropdown:v},data(){const e=(e,a,t)=>{""===a?(this.$message({message:e.field+"为必传项",type:"error"}),t(new Error(e.field+"为必传项"))):t()};return{loading:!1,favoriteForm:Object.assign({},b),rules:{type:[{validator:e}],ids:[{validator:e}]},dataMap:{movie:"",book:"",game:""},options:g,tempRoute:{}}},created(){this.tempRoute=Object.assign({},this.$route),a().then((e=>{this.dataMap=e.data.data,this.favoriteForm.ids=this.dataMap[this.favoriteForm.type]}))},methods:{setTagsViewTitle(){const e=Object.assign({},this.tempRoute,{title:`编辑收藏-${this.type}`});this.$store.dispatch("updateVisitedView",e)},changeType(e){this.favoriteForm.ids=this.dataMap[e]},submitForm(){this.$refs.favoriteForm.validate(((e,a)=>{if(!e)return!1;{this.loading=!0;let e=this,a=Object.assign({},this.favoriteForm);t(a).then((()=>{e.$notify({title:"成功",message:"发布成功",type:"success",duration:2e3}),this.loading=!1})).catch((e=>{}))}}))}}},F={class:"createFavorite-container"},j=f("更新"),k={class:"createFavorite-main-container"};var V=e(y,[["render",function(e,a,t,f,v,h){const b=s("el-button"),g=s("sticky"),y=s("el-option"),V=s("el-select"),_=s("el-form-item"),x=s("el-input"),$=s("el-form"),w=o("loading");return d(),i("div",F,[l($,{ref:"favoriteForm",model:v.favoriteForm,rules:v.rules,class:"form-container"},{default:r((()=>[l(g,{"class-name":"sub-navbar draft"},{default:r((()=>[n((d(),m(b,{style:{"margin-left":"10px"},type:"success",onClick:h.submitForm},{default:r((()=>[j])),_:1},8,["onClick"])),[[w,v.loading]])])),_:1}),u("div",k,[l(_,{label:"Type",prop:"type"},{default:r((()=>[l(V,{modelValue:v.favoriteForm.type,"onUpdate:modelValue":a[0]||(a[0]=e=>v.favoriteForm.type=e),class:"m-2",placeholder:"Select",size:"large",onChange:h.changeType},{default:r((()=>[(d(!0),i(p,null,c(v.options,(e=>(d(),m(y,{key:e.value,label:e.label,value:e.value},null,8,["label","value"])))),128))])),_:1},8,["modelValue","onChange"])])),_:1}),l(_,{label:"IDS",prop:"ids"},{default:r((()=>[l(x,{modelValue:v.favoriteForm.ids,"onUpdate:modelValue":a[1]||(a[1]=e=>v.favoriteForm.ids=e),rows:5,type:"textarea",placeholder:"Please input douban subject ids. Use commas to separate (don't use Chinese commas)"},null,8,["modelValue"])])),_:1})])])),_:1},8,["model","rules"])])}],["__scopeId","data-v-497ad9b6"]]);export{V as default};

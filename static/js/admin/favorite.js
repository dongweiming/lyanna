import{_ as e,e as a,ad as l,ae as t,j as i,P as o,k as s,c as d,l as n,p as r,J as m,x as u,n as c,$ as p,a0 as f,q as g,b as h,A as b,B as v}from"./index.js";import{D as V}from"./index5.js";import{S as y}from"./index4.js";const _={type:"movie",items:[]},w=[{value:"movie",label:"Movie"},{value:"book",label:"Book"},{value:"game",label:"Game"}];a();const k={name:"favorite",components:{Sticky:y,Dropdown:V},data(){const e=(e,a,l)=>{""===a?(this.$message({message:e.field+"为必传项",type:"error"}),l(new Error(e.field+"为必传项"))):l()};return{loading:!1,favoriteForm:Object.assign({},_),rules:{type:[{validator:e}],ids:[{validator:e}]},dataMap:{movie:"",book:"",game:""},options:w,tempRoute:{},dialogVisible:!1,dialog:{id:"",title:"",rating:0,comment:""},isAdd:!1}},created(){this.tempRoute=Object.assign({},this.$route),l().then((e=>{this.dataMap=e.data.data,this.favoriteForm.items=this.dataMap[this.favoriteForm.type]}))},methods:{setTagsViewTitle(){const e=Object.assign({},this.tempRoute,{title:`编辑收藏-${this.type}`});this.$store.dispatch("tagsView/updateVisitedView",e)},changeType(e){this.favoriteForm.items=this.dataMap[e]},edit(e){this.dialogVisible=!0,this.dialog=e,this.isAdd=!1},add(){this.dialogVisible=!0,this.isAdd=!0},confirm(){this.isAdd&&this.favoriteForm.items.unshift(Object.assign({},this.dialog)),this.handleClose()},handleClose(){this.dialogVisible=!1,this.dialog={id:"",title:"",rating:0,comment:""},this.isAdd=!1},submitForm(){this.$refs.favoriteForm.validate(((e,a)=>{if(!e)return!1;{this.loading=!0;let e=this,a=Object.assign({},this.favoriteForm);t(a).then((()=>{e.$notify({title:"成功",message:"发布成功",type:"success",duration:2e3}),this.loading=!1})).catch((e=>{}))}}))}}},C=e=>(b("data-v-497ad9b6"),e=e(),v(),e),F={class:"createFavorite-container"},x=h("更新"),j={class:"createFavorite-main-container"},A=C((()=>r("label",{for:"type",class:"el-form-item__label type-label"},"Type",-1))),U=h("Add"),T={class:"app-container"},$={key:0,class:"subject-link"},R=["href"],M={key:1},O=h("Edit"),D={class:"dialog-footer"},P=h("Cancel"),I=h("Confirm");var S=e(k,[["render",function(e,a,l,t,h,b){const v=i("el-button"),V=i("sticky"),y=i("el-option"),_=i("el-select"),w=i("el-form-item"),k=i("el-form"),C=i("el-table-column"),S=i("el-rate"),z=i("svg-icon"),B=i("el-table"),E=i("el-input"),q=i("el-dialog"),G=o("loading");return c(),s("div",F,[d(k,{ref:"favoriteForm",model:h.favoriteForm,rules:h.rules,class:"form-container"},{default:n((()=>[d(V,{"class-name":"sub-navbar draft"},{default:n((()=>[m((c(),u(v,{style:{"margin-left":"10px"},type:"success",onClick:b.submitForm},{default:n((()=>[x])),_:1},8,["onClick"])),[[G,h.loading]])])),_:1}),r("div",j,[d(w,{label:"",prop:"type"},{default:n((()=>[A,d(_,{modelValue:h.favoriteForm.type,"onUpdate:modelValue":a[0]||(a[0]=e=>h.favoriteForm.type=e),class:"m-2",placeholder:"Select",size:"large",onChange:b.changeType},{default:n((()=>[(c(!0),s(p,null,f(h.options,(e=>(c(),u(y,{key:e.value,label:e.label,value:e.value},null,8,["label","value"])))),128))])),_:1},8,["modelValue","onChange"]),d(v,{type:"primary",class:"btn-add",onClick:b.add},{default:n((()=>[U])),_:1},8,["onClick"])])),_:1})])])),_:1},8,["model","rules"]),r("div",T,[m((c(),u(B,{data:h.favoriteForm.items,border:"",fit:"","highlight-current-row":"",style:{width:"100%"}},{default:n((()=>[d(C,{align:"center",label:"ID",width:"80"},{default:n((e=>[r("span",null,g(e.row.id),1)])),_:1}),d(C,{width:"180px",align:"center",label:"Title"},{default:n((e=>[e.row.url?(c(),s("span",$,[r("a",{href:e.row.url,target:"_blank"},g(e.row.title),9,R)])):(c(),s("span",M,g(e.row.title),1))])),_:1}),d(C,{width:"180px",align:"center",label:"Rating"},{default:n((e=>[r("span",null,[d(S,{modelValue:e.row.rating,"onUpdate:modelValue":a=>e.row.rating=a,"allow-half":"",disabled:""},null,8,["modelValue","onUpdate:modelValue"])])])),_:1}),d(C,{align:"center",label:"Comment"},{default:n((e=>[r("span",null,g(e.row.comment),1)])),_:1}),d(C,{label:"Actions",align:"center",width:"230","class-name":"small-padding fixed-width"},{default:n((e=>[d(v,{type:"primary",size:"small",onClick:a=>b.edit(e.row)},{default:n((()=>[d(z,{"icon-class":"edit"}),O])),_:2},1032,["onClick"])])),_:1})])),_:1},8,["data"])),[[G,h.loading]])]),d(q,{modelValue:h.dialogVisible,"onUpdate:modelValue":a[5]||(a[5]=e=>h.dialogVisible=e),title:"Favorite",width:"30%","before-close":b.handleClose},{footer:n((()=>[r("span",D,[d(v,{onClick:b.handleClose},{default:n((()=>[P])),_:1},8,["onClick"]),d(v,{type:"primary",onClick:b.confirm},{default:n((()=>[I])),_:1},8,["onClick"])])])),default:n((()=>[d(k,{ref:"dialogFormRef",model:h.dialog,"status-icon":"","label-width":"120px",class:"dialogForm"},{default:n((()=>[d(w,{label:"ID",prop:"id"},{default:n((()=>[d(E,{modelValue:h.dialog.id,"onUpdate:modelValue":a[1]||(a[1]=e=>h.dialog.id=e),placeholder:"Please input"},null,8,["modelValue"])])),_:1}),d(w,{label:"Title",prop:"title"},{default:n((()=>[d(E,{modelValue:h.dialog.title,"onUpdate:modelValue":a[2]||(a[2]=e=>h.dialog.title=e),placeholder:"Please input"},null,8,["modelValue"])])),_:1}),d(w,{label:"Comment",prop:"comment"},{default:n((()=>[d(E,{modelValue:h.dialog.comment,"onUpdate:modelValue":a[3]||(a[3]=e=>h.dialog.comment=e),rows:3,type:"textarea",placeholder:"Please input"},null,8,["modelValue"])])),_:1}),d(w,{label:"Rating",prop:"rating"},{default:n((()=>[d(S,{modelValue:h.dialog.rating,"onUpdate:modelValue":a[4]||(a[4]=e=>h.dialog.rating=e),"allow-half":""},null,8,["modelValue"])])),_:1})])),_:1},8,["model"])])),_:1},8,["modelValue","before-close"])])}],["__scopeId","data-v-497ad9b6"]]);export{S as default};

const setting = {
  /*page layout related*/
  //sideBar or navbar show title
  title: 'Lyanna Admin',
  /**
   * @type {boolean} true | false
   * @description Whether show the logo in sidebar
   */
  sidebarLogo: true,
  /**
   * @type {boolean} true | false
   * @description Whether show the drop-down
   */
  ShowDropDown: true,
  /**
   * @type {boolean} true | false
   * @description Whether show Hamburger
   */
  showHamburger: true,
  /**
   * @type {boolean} true | false
   * @description Whether show the settings right-panel
   */
  showLeftMenu: true,
  /**
   * @type {boolean} true | false
   * @description Whether show TagsView
   */
  showTagsView: true,
  /**
   * @description TagsView show number
   */
  tagsViewNum: 6,
  /**
   * @type {boolean} true | false
   * @description Whether show the top Navbar
   */
  showTopNavbar: true,
  /* page  animation related*/
  /**
   * @type {boolean} true | false
   * @description Whether need animation of main area
   */
  mainNeedAnimation: true,
  /**
   * @type {boolean} true | false
   * @description Whether need nprogress
   */
  isNeedNprogress: true,

  /*page login or other*/
  /**
   * @type {boolean} true | false
   * @description Whether need login
   */
  isNeedLogin: true,
  /*
   * table height(100vh-delWindowHeight)
   * */
  delWindowHeight: '210px',
  /*
   * setting dev token when  isNeedLogin is setting false
   * */
  tmpToken: 'tmp_token',

  /*
   * vite.config.js base config
   * such as
   * */
  viteBasePath: '/'
}

export default setting

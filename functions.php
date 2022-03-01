<?php

function code2center_widgets_init() {
    register_sidebar( array(
        'name'          => __( 'Widget Area', 'code2center' ),
        'id'            => 'sidebar-1',
        'description'   => __( 'Add widgets here to appear in your sidebar.', 'code2center' ),
        'before_widget' => '<aside id="%1$s" class="widget %2$s">',
        'after_widget'  => '</aside>',
        'before_title'  => '<h2 class="widget-title">',
        'after_title'   => '</h2>',
    ) );
}
add_action( 'widgets_init', 'code2center_widgets_init' );

function code2center_widgets_init_german() {
    register_sidebar( array(
        'name'          => __( 'Widget Area', 'code2center' ),
        'id'            => 'sidebar-german',
        'description'   => __( 'Add widgets here to appear in your sidebar.', 'code2center' ),
        'before_widget' => '<aside id="%1$s" class="widget %2$s">',
        'after_widget'  => '</aside>',
        'before_title'  => '<h2 class="widget-title">',
        'after_title'   => '</h2>',
    ) );
}
add_action( 'widgets_init', 'code2center_widgets_init_german' );


function register_my_menus() {
  register_nav_menus(
    array('header-menu' => __( 'Main Menu 1', 'code2center' ) )
  );
}

add_action( 'init', 'register_my_menus' );

$markup = array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'post-thumbnails', );
add_theme_support( 'html5', $markup );	

add_filter( 'use_default_gallery_style', '__return_false' );

function code2center_scripts() {
wp_enqueue_style( 'code2center-style', get_stylesheet_uri() );
}

add_action( 'wp_enqueue_scripts', 'code2center_scripts' );

add_theme_support( 'title-tag' );

add_theme_support( 'post-formats', array( 'gallery', 'video', 'audio', 'aside' ) );

function rt_before_after($content) {
    $parents = get_post_ancestors( $post->ID );
    foreach ($parents as $value) {
    $title = get_the_title($value);
    $page_link = get_page_link($value);
    $page_url = '<a href=' . $page_link .'>' . $title . '</a>';
    $item_output1 = $page_url .' -> '. $item_output1;
    }
   
    $title2 = get_the_title($post->ID);
    $page_link2 = get_page_link($post->ID);
    $page_url2 = '<a href=' . $page_link2 .'>' . $title2 . '</a>';
    $url = get_permalink(get_option('page_for_posts' ));
    $title3 = get_the_title($url);
    $page_url3 = '<a href=' . $url .'>' . 'Home' . '</a>';
    $beforecontent = '<h2>' . $page_url3 .' -> '. $item_output1 . $title2 . '</h2>';

    //$aftercontent = 'And this will come after.';
    $aftercontent = '';
    $fullcontent = $beforecontent .'<br>' . '<br>' . $content . $aftercontent;
	if ( is_page()  and !is_front_page() ) {
    return $fullcontent;
	}
	else {
		return $content;
	}
}
add_filter('the_content', 'rt_before_after');
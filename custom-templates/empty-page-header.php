<?php
/*
Template Name: Empty Page Header Template

Basic template with centered content and header included
*/
?>

<style type="text/css">
body {
width: 900px;
margin-left: auto;
margin-right: auto;
}
</style>

<?php wp_head(); ?>




<title><?php echo esc_html(get_the_title()); ?></title>

<h2><a href="/">Home</a></h2>

<?php the_content(); ?>

<?php get_footer(); ?>

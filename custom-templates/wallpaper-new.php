<?php
/*
Template Name: Wallpaper New
*/
?>


<body <?php body_class(); ?>>
<?php wp_body_open(); ?>


<div id="main">
<div id="header">
<a href="/blog"><img src="<?php echo get_template_directory_uri(); ?>/images/mclogo2.jpg" /></a>
<?php get_header(); ?>
	    
</div>

<div id="sidebar"> 

<?php wp_nav_menu(array('menu' => 'Wallpaper')); ?>
</div>

<div id="content">


<?php if (have_posts()) : ?><?php while (have_posts()) : the_post(); ?>
<div class="post">
<?php the_content('-> read more'); ?>

<?php endwhile; ?>

<?php endif; ?>
</div>
</div>
</div>

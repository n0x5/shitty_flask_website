<?php
/*
Template Name: Gallery Index Paginated
*/
?>

<body>
<style type="text/css">
.mainbody {
width: 800px;
margin-left: auto;
margin-right: auto;
}
body {
background-color: black;
color: white;
}
.post-entry {
}
.categoryl {
height: 1045px;
width: 430px;
float: left;
}

.category2 {
height: 100px;
width: 430px;
display: block;
}
a.titlecat2 {
font-size: 13px;
color: #e91e63;
}
a.titlecat3 {
font-size: 13px;
color: white;
}
h2 {
text-align: center;
}
a {
color: white;
text-decoration: none;
}
a:visited {
color: #c1c1c1;
}
.grid-item {
}
a.titlecat {
font-size: 30px;
color: #e91e63;
}

.headtitle {
text-align: center;
font-size: 80px;
}
.descr {
text-align: center;
font-size: 20px;
}

p.recent {
font-size: 12px;
}
.banner{
margin-bottom: 20px;
}
.galleries {
    width: 186;
height: 250px;
float: left;
}

.gallerytitle {
font-size: 20px;
}
.galleryinfo {
 color: gray;
font-size: 12px;
}
.pagination {
font-size: 25px;
text-align: center;
width: 100%;
display: inline-block;
margin-left: auto;
margin-right: auto;
font-size: 35px;
letter-spacing: 5px;
margin-bottom: 25px;
}
}

</style>
    
    
<title><?php echo esc_html(get_the_title()); ?></title>
<div class="mainbody">


<div class="banner"><?php // echo get_the_post_thumbnail($post_id, 'large', array( 'class' => 'alignleft' )); ?></div>


<?php the_content(); ?>

<?php 

$paged = get_query_var( 'paged', 1 );

// orderby modified = repeated/duplicate posts in pagination
$args = array(
'post_parent' => $post->ID,
'post_type' => 'page',
'orderby' => 'date',
'meta_key' => '_thumbnail_id',
'paged' => $paged
);

$the_query = new WP_Query( $args ); ?>


<?php if ( $the_query->have_posts() ) : ?>

<?php while ( $the_query->have_posts() ) : $the_query->the_post(); ?>
<?php
$wp_query2 = new WP_Query(array(
'post_parent' => $post->ID,
'post_type' => 'attachment',
'post_status' => 'inherit',
'post_mime_type' => 'image'
));
?>

<?php echo '<div class="galleries"> <a href="'.get_permalink().'" title="'.get_the_title().'">'.get_the_post_thumbnail($post_id, 'thumbnail', array( 'class' => 'alignleft' )).'</a>'.'<div class="gallerytitle"><a href="'.get_permalink().'">'.get_the_title().'</a></div>'; ?> <div class="galleryinfo"> Updated: <?php the_modified_date(); ?> </div><?php $count = $wp_query2->found_posts; echo $count . ' images' ?> </div>

<?php endwhile; ?>
	<?php // echo 'Currently Browsing Page ', $paged; ?>
<div class="pagination">
<?php

echo paginate_links( array(
    //'base' => str_replace( $big, '%#%', esc_url( get_pagenum_link( $big ) ) ),
    //'format' => '?paged=%#%',
    //'current' => $paged,
    'total' => $the_query->max_num_pages,
    'prev_next'    => true,
    'prev_text'    => sprintf( '<i></i> %1$s', __( '<-', 'text-domain' ) ),
    'next_text'    => sprintf( '%1$s <i></i>', __( '->', 'text-domain' ) ),
) );
?>
</div>
    
<?php wp_reset_postdata(); ?>

<?php else : ?>
    <p><?php _e( 'Sorry, no posts matched your criteria.' ); ?></p>
<?php endif; ?>


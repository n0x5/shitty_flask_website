<?php
/*
Template Name: All Activity
*/
?>

<?php
$args = array(
'post_type' => array( 'post', 'page', 'revision', 'attachment', 'nav_menu_item' ),
'post_status' => 'any',
'posts_per_page' => 500,
);

$the_query = new WP_Query( $args ); ?>


<?php if ( $the_query->have_posts() ) : ?>

<?php while ( $the_query->have_posts() ) : $the_query->the_post(); ?>

<p><?php the_time('F jS, Y') ?> - <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></p>
<?php endwhile; ?>

<?php else : ?>
    <p><?php _e( 'Sorry, no posts matched your criteria.' ); ?></p>
<?php endif; ?>
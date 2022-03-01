<?php
/*
Template Name: Girls Page
*/
?>

<title><?php echo esc_html(get_the_title()); ?></title>
<h2><a href="/">Home</a> -> <?php the_title(''); ?></h2>

<?php

$paged = ( get_query_var( 'paged' ) ) ? absint( get_query_var( 'paged' ) ) : 1;

$args = array(
'post_type' => 'page',
'post_status' => 'publish',
'meta_key'     => 'girls',
'orderby' => array('date' => 'desc'),
'paged' => $paged,
);

$the_query = new WP_Query( $args ); ?>


<?php if ( $the_query->have_posts() ) : ?>

<?php while ( $the_query->have_posts() ) : $the_query->the_post(); ?>
<p><?php echo get_the_post_thumbnail( $post_id, 'thumbnail', array( 'class' => 'alignleft' ) ); ?> <?php the_time('F jS, Y') ?> - <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></p>
<?php endwhile; ?>

<?php
$big = 999999999;

echo paginate_links( array(
    'base' => str_replace( $big, '%#%', esc_url( get_pagenum_link( $big ) ) ),
    'format' => '?paged=%#%',
    'current' => max( 1, get_query_var('paged') ),
    'total' => $the_query->max_num_pages
) );
?>

    <?php wp_reset_postdata(); ?>

<?php else : ?>
    <p><?php _e( 'Sorry, no posts matched your criteria.' ); ?></p>
<?php endif; ?>



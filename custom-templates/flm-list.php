<?php
/*
Template Name: FLM Films list
*/
?>
<?php get_header(); ?>

<h2>FLM Films</h2>
<?php

$args = array(
'post_parent' => $post->ID,
'post_type' => 'page',
'post_status' => 'any',
'posts_per_page' => 10,
);

$the_query = new WP_Query( $args ); ?>


<?php if ( $the_query->have_posts() ) : ?>

<?php while ( $the_query->have_posts() ) : $the_query->the_post(); ?>


<table style="border-collapse: collapse;">
<tbody>
<tr>
<td style="border: 1px solid #316291;"><?php echo get_the_post_thumbnail( $post_id, 'medium'); ?><h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2></td>

<td style="border: 1px solid #316291;">
<?php
$blocks = parse_blocks(get_the_content());
foreach ( $blocks as $block ) {
    if (strpos($block['innerHTML'], 'Infobox') !== false) {
    echo $block['innerHTML'];
    }
}
//echo var_dump($blocks);

?>
</td>
</tr>
</tbody>
</table>
<br>
<?php endwhile; ?>

<?php else : ?>
    <p><?php _e( 'Sorry, no posts matched your criteria.' ); ?></p>
<?php endif; ?>

<?php get_footer(); ?>
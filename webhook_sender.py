from datetime import datetime

from discord_webhook import DiscordWebhook, DiscordEmbed

import config

class WebhookSender:

    @staticmethod
    def send_job(webhook_url, url, is_remote, job_title, company, location, description, attributes, benefits, posted_timestamp, easy_apply, source,
                 top_job_role_id, good_job_role_id, easy_apply_role_id,
                 ai_overview):

        content = ''

        if ai_overview['fit_score'] >= config.top_job_min_ai_score:
            content += f'<@&{top_job_role_id}>'

        if ai_overview['apply'] == 'YES':
            if ai_overview['fit_score'] >= config.top_job_min_ai_score:
                content += f'<@&{top_job_role_id}>'
            else:
                content += f'<@&{good_job_role_id}>'

        if easy_apply:
            content += f'<@&{easy_apply_role_id}>'

        webhook = DiscordWebhook(content=content, url=webhook_url)

        embed_description = ''

        embed_description += f'\n\n**Company:** {company}'
        embed_description += f'\n**Location:** {location if location is not None else ''}{f" Remote" if is_remote else ''}'
        embed_description += f'\n**Posted Date:** <t:{round(posted_timestamp)}:R>'

        embed_description += f'\n**Source:** {source}'

        main_embed = DiscordEmbed(title=job_title,
                             description=embed_description,
                             url=url)

        overview_description = ''

        overview_description += f'**AI Fit Score:** {ai_overview["fit_score"]}/100'
        overview_description += f'\n**Seniority Risk:** {ai_overview["seniority_risk"]}'

        overview_description += f'\n\n**Apply:** {ai_overview["apply"]}'
        overview_description += f'\n**Reason:** {ai_overview["apply_reason"]}'

        overview_description += f'\n\n**Missing Skills:**'
        for i in ai_overview["missing_skills"]:
            overview_description += f'\n- *{i}*'

        overview_description += f'\n\n**Matching Skills:**'
        for i in ai_overview["matching_skills"]:
            overview_description += f'\n- *{i}*'

        overview_description += f'\n\n*{ai_overview["overview"]}*'

        ai_embed = DiscordEmbed(title='AI OVERVIEW',
                             description=overview_description)

        embed_color = '7883ad'

        for score in list(config.fit_score_ember_colors.keys())[::-1]:
            if ai_overview["fit_score"] >= score:
                embed_color = config.fit_score_ember_colors[score]
                break

        main_embed.set_color(embed_color)
        ai_embed.set_color(embed_color)

        webhook.add_embed(main_embed)
        webhook.add_embed(ai_embed)

        response = webhook.execute()

        return response

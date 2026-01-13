from datetime import datetime

from discord_webhook import DiscordWebhook, DiscordEmbed

import config

class WebhookSender:

    @staticmethod
    def send_job(webhook_url, url, apply_url, search_title, job_title, company, location, description, attributes, benefits, posted_timestamp, source, ai_data):
        webhook = DiscordWebhook(url=webhook_url)

        embed_description = ''

        # embed_description = f'*{description}*'
        embed_description += f'\n\n**Company:** {company}'
        embed_description += f'\n**Location:** {location}'
        embed_description += f'\n**Posted Date:** <t:{round(posted_timestamp)}:R>'
        # embed_description += f'\n**Benefits:** {", ".join(benefits)}'
        # embed_description += f'\n**Attributes:** {", ".join(attributes)}'

        embed_description += f'\n\n**Search title:** {search_title}'
        embed_description += f'\n**Source:** {source}'

        embed_description += f'\n\n*[Apply Url]({apply_url})*'


        main_embed = DiscordEmbed(title=job_title,
                             description=embed_description,
                             url=url)

        overview_description = ''

        overview_description += f'**AI Fit Score:** {ai_data["fit_score"]}/100'
        overview_description += f'\n**Seniority Risk:** {ai_data["seniority_risk"]}'

        overview_description += f'\n\n**Apply:** {ai_data["apply"]}'
        overview_description += f'\n**Reason:** {ai_data["apply_reason"]}'

        overview_description += f'\n\n**Missing Skills:**'
        for i in ai_data["missing_skills"]:
            overview_description += f'\n- *{i}*'

        overview_description += f'\n\n**Matching Skills:**'
        for i in ai_data["matching_skills"]:
            overview_description += f'\n- *{i}*'

        overview_description += f'\n\n*{ai_data["overview"]}*'

        ai_embed = DiscordEmbed(title='AI OVERVIEW',
                             description=overview_description)

        embed_color = '7883ad'

        for score in list(config.fit_score_ember_colors.keys())[::-1]:
            if ai_data["fit_score"] >= score:
                embed_color = config.fit_score_ember_colors[score]
                break

        main_embed.set_color(embed_color)
        ai_embed.set_color(embed_color)

        webhook.add_embed(main_embed)
        webhook.add_embed(ai_embed)

        response = webhook.execute()

        return response

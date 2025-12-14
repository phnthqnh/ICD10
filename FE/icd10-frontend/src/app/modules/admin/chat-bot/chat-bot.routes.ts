import { inject } from '@angular/core';
import { ActivatedRouteSnapshot, Router, RouterStateSnapshot, Routes } from '@angular/router';
import { ChatBotComponent } from './chat-bot.component';
import { ChatBotService } from 'app/core/chat-bot/chat-bot.services';
import { ChatSessionComponent } from './chat-session/chat-session.component';
import { ChatMessageComponent } from './chat-message/chat-message.component';
import { EmptyMessageComponent } from './empty-message/empty-message.component';
import { catchError, throwError } from 'rxjs';

/**
 * Chat message resolver
 *
 * @param route
 * @param state
 */
const ChatMessageResolver = (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) =>
{
    const chatService = inject(ChatBotService);
    const router = inject(Router);
    const chatId = Number(route.paramMap.get('id'));
    return chatService.getChatMessage(chatId).pipe(
        // Error here means the requested chat is not available
        catchError((error) =>
        {
            // Log the error
            console.error(error);

            // Get the parent url
            const parentUrl = state.url.split('/').slice(0, -1).join('/');

            // Navigate to there
            router.navigateByUrl(parentUrl);

            // Throw an error
            return throwError(error);
        }),
    );
};

export default [
    {
        path     : '',
        component: ChatBotComponent,
        resolve  : {
            chat_session   : () => inject(ChatBotService).getUserChatSessionList(),
        },
        children : [
            {
                path     : '',
                component: ChatSessionComponent,
                children : [
                    {
                        path     : '',
                        pathMatch: 'full',
                        component: EmptyMessageComponent,
                    },
                    {
                        path     : ':id',
                        component: ChatMessageComponent,
                        resolve  : {
                            chatmessage: ChatMessageResolver,
                        },
                    },
                ],
            },
        ],
    },
] as Routes;
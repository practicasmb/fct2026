import { ChangeDetectionStrategy, Component } from '@angular/core';
// Solo se importan los módulos propios de la tabla


@Component({
  selector: 'app-root',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [

  ],
  templateUrl: './app.html',
})
export class AppComponent {
}